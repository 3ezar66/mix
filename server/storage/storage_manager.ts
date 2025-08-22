import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { Pool } from 'pg';
import { eq, and, desc, sql } from 'drizzle-orm';
import { Logger } from '../utils/logger';
import { CacheManager } from '../utils/cache';
import { devices, scanResults, alerts } from './schema';

// Define database schema types
interface Device {
    id: string;
    ip: string;
    mac: string;
    hostname: string;
    first_seen: Date;
    last_seen: Date;
    status: 'active' | 'inactive' | 'blocked';
}

interface ScanResult {
    id: string;
    device_id: string;
    timestamp: Date;
    is_mining: boolean;
    confidence: number;
    ports: number[];
    mining_pools: string[];
    resource_usage: ResourceUsage;
}

interface ResourceUsage {
    cpu_usage: number;
    memory_usage: number;
    gpu_usage?: number;
    network_upload: number;
    network_download: number;
}

interface Alert {
    id: string;
    device_id: string;
    timestamp: Date;
    type: string;
    severity: 'low' | 'medium' | 'high';
    message: string;
    resolved: boolean;
}

export class StorageManager {
    private static instance: StorageManager;
    private pool: Pool;
    private db: any; // drizzle instance
    private logger: Logger;
    private cache: CacheManager;
    private readonly CACHE_TTL = 300; // 5 minutes

    private constructor() {
        this.logger = Logger.getInstance('StorageManager');
        this.cache = CacheManager.getInstance();
        this.pool = new Pool({
            host: process.env.DB_HOST || 'localhost',
            port: parseInt(process.env.DB_PORT || '5432'),
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME,
        });
        this.db = drizzle(this.pool);
        this.initializeDatabase();
    }

    public static getInstance(): StorageManager {
        if (!StorageManager.instance) {
            StorageManager.instance = new StorageManager();
        }
        return StorageManager.instance;
    }

    private async initializeDatabase(): Promise<void> {
        try {
            // Run migrations
            await migrate(this.db, { migrationsFolder: './migrations' });
            this.logger.info('Database initialized successfully');
        } catch (error) {
            this.logger.error('Database initialization failed', { error: error as Error });
            throw error;
        }
    }

    // Device Management
    public async upsertDevice(device: Partial<Device>): Promise<Device> {
        try {
            const result = await this.db.insert(devices)
                .values({
                    ...device,
                    last_seen: new Date(),
                })
                .onConflict('ip')
                .merge()
                .returning();

            const savedDevice = result[0];
            this.cache.set(`device_${savedDevice.ip}`, savedDevice, this.CACHE_TTL);
            return savedDevice;
        } catch (error) {
            this.logger.error('Error upserting device', { error: error as Error, device });
            throw error;
        }
    }

    public async getDevice(ip: string): Promise<Device | null> {
        try {
            // Check cache first
            const cachedDevice = this.cache.get<Device>(`device_${ip}`);
            if (cachedDevice) return cachedDevice;

            const result = await this.db
                .select()
                .from(devices)
                .where(eq(devices.ip, ip));

            const device = result[0] || null;
            if (device) {
                this.cache.set(`device_${ip}`, device, this.CACHE_TTL);
            }
            return device;
        } catch (error) {
            this.logger.error('Error getting device', { error: error as Error, ip });
            throw error;
        }
    }

    // Scan Results Management
    public async saveScanResult(result: Partial<ScanResult>): Promise<ScanResult> {
        try {
            const savedResult = await this.db
                .insert(scanResults)
                .values({
                    ...result,
                    timestamp: new Date(),
                })
                .returning();

            // Update device last_seen
            await this.upsertDevice({
                ip: result.device_id,
                last_seen: new Date(),
            });

            return savedResult[0];
        } catch (error) {
            this.logger.error('Error saving scan result', { error: error as Error, result });
            throw error;
        }
    }

    public async getDeviceScanHistory(deviceId: string, limit: number = 10): Promise<ScanResult[]> {
        try {
            const cacheKey = `scan_history_${deviceId}_${limit}`;
            const cachedHistory = this.cache.get<ScanResult[]>(cacheKey);
            if (cachedHistory) return cachedHistory;

            const results = await this.db
                .select()
                .from(scanResults)
                .where(eq(scanResults.device_id, deviceId))
                .orderBy(desc(scanResults.timestamp))
                .limit(limit);

            this.cache.set(cacheKey, results, this.CACHE_TTL);
            return results;
        } catch (error) {
            this.logger.error('Error getting device scan history', { error: error as Error, deviceId });
            throw error;
        }
    }

    // Alert Management
    public async createAlert(alert: Partial<Alert>): Promise<Alert> {
        try {
            const savedAlert = await this.db
                .insert(alerts)
                .values({
                    ...alert,
                    timestamp: new Date(),
                    resolved: false,
                })
                .returning();

            return savedAlert[0];
        } catch (error) {
            this.logger.error('Error creating alert', { error: error as Error, alert });
            throw error;
        }
    }

    public async getActiveAlerts(): Promise<Alert[]> {
        try {
            const cacheKey = 'active_alerts';
            const cachedAlerts = this.cache.get<Alert[]>(cacheKey);
            if (cachedAlerts) return cachedAlerts;

            const activeAlerts = await this.db
                .select()
                .from(alerts)
                .where(eq(alerts.resolved, false))
                .orderBy(desc(alerts.timestamp));

            this.cache.set(cacheKey, activeAlerts, this.CACHE_TTL);
            return activeAlerts;
        } catch (error) {
            this.logger.error('Error getting active alerts', { error: error as Error });
            throw error;
        }
    }

    // Data Cleanup
    public async cleanupOldData(retentionDays: number = 30): Promise<void> {
        try {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

            // Delete old scan results
            await this.db
                .delete(scanResults)
                .where(sql`timestamp < ${cutoffDate}`);

            // Delete old resolved alerts
            await this.db
                .delete(alerts)
                .where(
                    and(
                        sql`timestamp < ${cutoffDate}`,
                        eq(alerts.resolved, true)
                    )
                );

            // Delete inactive devices
            await this.db
                .delete(devices)
                .where(sql`last_seen < ${cutoffDate}`);

            this.logger.info('Data cleanup completed', { retentionDays });
        } catch (error) {
            this.logger.error('Error during data cleanup', { error: error as Error, retentionDays });
            throw error;
        }
    }

    // Statistics and Analytics
    public async getSystemStats(): Promise<any> {
        try {
            const cacheKey = 'system_stats';
            const cachedStats = this.cache.get(cacheKey);
            if (cachedStats) return cachedStats;

            const [deviceCount, minerCount, alertCount] = await Promise.all([
                this.db.select().from(devices).execute(),
                this.db
                    .select()
                    .from(scanResults)
                    .where(eq(scanResults.is_mining, true))
                    .execute(),
                this.db
                    .select()
                    .from(alerts)
                    .where(eq(alerts.resolved, false))
                    .execute(),
            ]);

            const stats = {
                totalDevices: deviceCount.length,
                activeMiners: minerCount.length,
                pendingAlerts: alertCount.length,
                lastUpdate: new Date(),
            };

            this.cache.set(cacheKey, stats, this.CACHE_TTL);
            return stats;
        } catch (error) {
            this.logger.error('Error getting system stats', { error: error as Error });
            throw error;
        }
    }

    // Database Health Check
    public async healthCheck(): Promise<boolean> {
        try {
            await this.pool.query('SELECT 1');
            return true;
        } catch (error) {
            this.logger.error('Database health check failed', { error: error as Error });
            return false;
        }
    }

    // Cleanup resources
    public async shutdown(): Promise<void> {
        try {
            await this.pool.end();
            this.logger.info('Database connection closed');
        } catch (error) {
            this.logger.error('Error during database shutdown', { error: error as Error });
            throw error;
        }
    }
}