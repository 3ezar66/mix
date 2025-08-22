import { drizzle } from 'drizzle-orm/node-postgres';
import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { Pool } from 'pg';
import { eq, and, desc, sql } from 'drizzle-orm';
import { Logger } from '../utils/logger';
import { CacheManager } from '../utils/cache';
import { devices, scanResults, alerts } from './schema';
export class StorageManager {
    static instance;
    pool;
    db; // drizzle instance
    logger;
    cache;
    CACHE_TTL = 300; // 5 minutes
    constructor() {
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
    static getInstance() {
        if (!StorageManager.instance) {
            StorageManager.instance = new StorageManager();
        }
        return StorageManager.instance;
    }
    async initializeDatabase() {
        try {
            // Run migrations
            await migrate(this.db, { migrationsFolder: './migrations' });
            this.logger.info('Database initialized successfully');
        }
        catch (error) {
            this.logger.error('Database initialization failed', { error: error });
            throw error;
        }
    }
    // Device Management
    async upsertDevice(device) {
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
        }
        catch (error) {
            this.logger.error('Error upserting device', { error: error, device });
            throw error;
        }
    }
    async getDevice(ip) {
        try {
            // Check cache first
            const cachedDevice = this.cache.get(`device_${ip}`);
            if (cachedDevice)
                return cachedDevice;
            const result = await this.db
                .select()
                .from(devices)
                .where(eq(devices.ip, ip));
            const device = result[0] || null;
            if (device) {
                this.cache.set(`device_${ip}`, device, this.CACHE_TTL);
            }
            return device;
        }
        catch (error) {
            this.logger.error('Error getting device', { error: error, ip });
            throw error;
        }
    }
    // Scan Results Management
    async saveScanResult(result) {
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
        }
        catch (error) {
            this.logger.error('Error saving scan result', { error: error, result });
            throw error;
        }
    }
    async getDeviceScanHistory(deviceId, limit = 10) {
        try {
            const cacheKey = `scan_history_${deviceId}_${limit}`;
            const cachedHistory = this.cache.get(cacheKey);
            if (cachedHistory)
                return cachedHistory;
            const results = await this.db
                .select()
                .from(scanResults)
                .where(eq(scanResults.device_id, deviceId))
                .orderBy(desc(scanResults.timestamp))
                .limit(limit);
            this.cache.set(cacheKey, results, this.CACHE_TTL);
            return results;
        }
        catch (error) {
            this.logger.error('Error getting device scan history', { error: error, deviceId });
            throw error;
        }
    }
    // Alert Management
    async createAlert(alert) {
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
        }
        catch (error) {
            this.logger.error('Error creating alert', { error: error, alert });
            throw error;
        }
    }
    async getActiveAlerts() {
        try {
            const cacheKey = 'active_alerts';
            const cachedAlerts = this.cache.get(cacheKey);
            if (cachedAlerts)
                return cachedAlerts;
            const activeAlerts = await this.db
                .select()
                .from(alerts)
                .where(eq(alerts.resolved, false))
                .orderBy(desc(alerts.timestamp));
            this.cache.set(cacheKey, activeAlerts, this.CACHE_TTL);
            return activeAlerts;
        }
        catch (error) {
            this.logger.error('Error getting active alerts', { error: error });
            throw error;
        }
    }
    // Data Cleanup
    async cleanupOldData(retentionDays = 30) {
        try {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
            // Delete old scan results
            await this.db
                .delete(scanResults)
                .where(sql `timestamp < ${cutoffDate}`);
            // Delete old resolved alerts
            await this.db
                .delete(alerts)
                .where(and(sql `timestamp < ${cutoffDate}`, eq(alerts.resolved, true)));
            // Delete inactive devices
            await this.db
                .delete(devices)
                .where(sql `last_seen < ${cutoffDate}`);
            this.logger.info('Data cleanup completed', { retentionDays });
        }
        catch (error) {
            this.logger.error('Error during data cleanup', { error: error, retentionDays });
            throw error;
        }
    }
    // Statistics and Analytics
    async getSystemStats() {
        try {
            const cacheKey = 'system_stats';
            const cachedStats = this.cache.get(cacheKey);
            if (cachedStats)
                return cachedStats;
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
        }
        catch (error) {
            this.logger.error('Error getting system stats', { error: error });
            throw error;
        }
    }
    // Database Health Check
    async healthCheck() {
        try {
            await this.pool.query('SELECT 1');
            return true;
        }
        catch (error) {
            this.logger.error('Database health check failed', { error: error });
            return false;
        }
    }
    // Cleanup resources
    async shutdown() {
        try {
            await this.pool.end();
            this.logger.info('Database connection closed');
        }
        catch (error) {
            this.logger.error('Error during database shutdown', { error: error });
            throw error;
        }
    }
}
