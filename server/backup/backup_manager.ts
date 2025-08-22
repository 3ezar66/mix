import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { Logger } from '../utils/logger';
import { StorageManager } from '../storage/storage_manager';
import { CacheManager } from '../utils/cache';

const execAsync = promisify(exec);

interface BackupConfig {
    backupDir: string;
    retentionDays: number;
    compressionLevel: number;
    maxBackups: number;
    scheduleHour: number;
    scheduleMinute: number;
}

interface BackupMetadata {
    timestamp: Date;
    size: number;
    type: 'full' | 'incremental';
    status: 'success' | 'failed';
    error?: string;
}

export class BackupManager {
    private static instance: BackupManager;
    private logger: Logger;
    private storage: StorageManager;
    private cache: CacheManager;
    private config: BackupConfig;
    private backupScheduler: NodeJS.Timeout | null;

    private constructor() {
        this.logger = Logger.getInstance('BackupManager');
        this.storage = StorageManager.getInstance();
        this.cache = CacheManager.getInstance();
        this.backupScheduler = null;

        // Default configuration
        this.config = {
            backupDir: path.join(process.cwd(), 'backups'),
            retentionDays: 30,
            compressionLevel: 9,
            maxBackups: 10,
            scheduleHour: 2, // 2 AM
            scheduleMinute: 0,
        };

        this.initialize();
    }

    public static getInstance(): BackupManager {
        if (!BackupManager.instance) {
            BackupManager.instance = new BackupManager();
        }
        return BackupManager.instance;
    }

    private async initialize(): Promise<void> {
        try {
            // Ensure backup directory exists
            if (!fs.existsSync(this.config.backupDir)) {
                fs.mkdirSync(this.config.backupDir, { recursive: true });
            }

            // Load configuration from file if exists
            const configPath = path.join(process.cwd(), 'config', 'backup.json');
            if (fs.existsSync(configPath)) {
                const configFile = fs.readFileSync(configPath, 'utf8');
                this.config = { ...this.config, ...JSON.parse(configFile) };
            }

            this.scheduleBackup();
            this.logger.info('Backup Manager initialized successfully');
        } catch (error) {
            this.logger.error('Failed to initialize Backup Manager', { error: error as Error });
            throw error;
        }
    }

    private scheduleBackup(): void {
        if (this.backupScheduler) {
            clearInterval(this.backupScheduler);
        }

        this.backupScheduler = setInterval(() => {
            const now = new Date();
            if (now.getHours() === this.config.scheduleHour && 
                now.getMinutes() === this.config.scheduleMinute) {
                this.createBackup('full')
                    .catch(error => this.logger.error('Scheduled backup failed', { error: error as Error }));
            }
        }, 60000); // Check every minute
    }

    public async createBackup(type: 'full' | 'incremental' = 'full'): Promise<BackupMetadata> {
        const timestamp = new Date();
        const backupFileName = `backup_${type}_${timestamp.toISOString().replace(/[:.]/g, '-')}.tar.gz`;
        const backupPath = path.join(this.config.backupDir, backupFileName);

        try {
            // Ensure database is in a consistent state
            await this.storage.healthCheck();

            // Create backup directory if it doesn't exist
            if (!fs.existsSync(this.config.backupDir)) {
                fs.mkdirSync(this.config.backupDir, { recursive: true });
            }

            // Perform database backup
            const dbConfig = {
                host: process.env.DB_HOST || 'localhost',
                port: process.env.DB_PORT || '5432',
                database: process.env.DB_NAME,
                user: process.env.DB_USER,
                password: process.env.DB_PASSWORD,
            };

            const pgDumpCmd = `PGPASSWORD=${dbConfig.password} pg_dump -h ${dbConfig.host} -p ${dbConfig.port} -U ${dbConfig.user} -d ${dbConfig.database} -F t | gzip -${this.config.compressionLevel} > ${backupPath}`;

            await execAsync(pgDumpCmd);

            // Get backup file size
            const stats = fs.statSync(backupPath);

            const metadata: BackupMetadata = {
                timestamp,
                size: stats.size,
                type,
                status: 'success',
            };

            // Save backup metadata
            this.saveBackupMetadata(metadata);

            // Cleanup old backups
            await this.cleanupOldBackups();

            this.logger.info('Backup created successfully', { metadata });
            return metadata;

        } catch (error) {
            const metadata: BackupMetadata = {
                timestamp,
                size: 0,
                type,
                status: 'failed',
                error: (error as Error).message,
            };

            this.saveBackupMetadata(metadata);
            this.logger.error('Backup creation failed', { error: error as Error, metadata });
            throw error;
        }
    }

    public async restoreBackup(backupFileName: string): Promise<void> {
        const backupPath = path.join(this.config.backupDir, backupFileName);

        try {
            // Verify backup file exists
            if (!fs.existsSync(backupPath)) {
                throw new Error(`Backup file not found: ${backupFileName}`);
            }

            // Stop all active connections
            await this.storage.shutdown();

            // Perform database restore
            const dbConfig = {
                host: process.env.DB_HOST || 'localhost',
                port: process.env.DB_PORT || '5432',
                database: process.env.DB_NAME,
                user: process.env.DB_USER,
                password: process.env.DB_PASSWORD,
            };

            const pgRestoreCmd = `gunzip -c ${backupPath} | PGPASSWORD=${dbConfig.password} pg_restore -h ${dbConfig.host} -p ${dbConfig.port} -U ${dbConfig.user} -d ${dbConfig.database} --clean --if-exists`;

            await execAsync(pgRestoreCmd);

            // Clear cache
            this.cache.flush();

            this.logger.info('Backup restored successfully', { backupFileName });

        } catch (error) {
            this.logger.error('Backup restoration failed', { error: error as Error, backupFileName });
            throw error;
        }
    }

    private async cleanupOldBackups(): Promise<void> {
        try {
            const backups = fs.readdirSync(this.config.backupDir)
                .filter(file => file.startsWith('backup_'))
                .map(file => ({
                    name: file,
                    path: path.join(this.config.backupDir, file),
                    time: fs.statSync(path.join(this.config.backupDir, file)).mtime.getTime()
                }))
                .sort((a, b) => b.time - a.time);

            // Remove old backups exceeding retention period
            const cutoffTime = Date.now() - (this.config.retentionDays * 24 * 60 * 60 * 1000);
            const oldBackups = backups.filter(backup => backup.time < cutoffTime);

            // Keep at least one backup regardless of age
            const backupsToDelete = backups.length > 1 ? oldBackups : [];

            // Remove excess backups if exceeding maxBackups
            if (backups.length > this.config.maxBackups) {
                backupsToDelete.push(...backups.slice(this.config.maxBackups));
            }

            // Delete backup files
            for (const backup of backupsToDelete) {
                fs.unlinkSync(backup.path);
                this.logger.info('Deleted old backup', { backup: backup.name });
            }

        } catch (error) {
            this.logger.error('Failed to cleanup old backups', { error: error as Error });
            throw error;
        }
    }

    private saveBackupMetadata(metadata: BackupMetadata): void {
        const metadataPath = path.join(this.config.backupDir, 'backup_metadata.json');
        try {
            let allMetadata: BackupMetadata[] = [];
            
            // Load existing metadata if available
            if (fs.existsSync(metadataPath)) {
                const existingData = fs.readFileSync(metadataPath, 'utf8');
                allMetadata = JSON.parse(existingData);
            }

            // Add new metadata
            allMetadata.push(metadata);

            // Save updated metadata
            fs.writeFileSync(metadataPath, JSON.stringify(allMetadata, null, 2));

        } catch (error) {
            this.logger.error('Failed to save backup metadata', { error: error as Error, metadata });
        }
    }

    public getBackupList(): BackupMetadata[] {
        const metadataPath = path.join(this.config.backupDir, 'backup_metadata.json');
        try {
            if (fs.existsSync(metadataPath)) {
                const data = fs.readFileSync(metadataPath, 'utf8');
                return JSON.parse(data);
            }
            return [];
        } catch (error) {
            this.logger.error('Failed to get backup list', { error: error as Error });
            return [];
        }
    }

    public updateConfig(newConfig: Partial<BackupConfig>): void {
        this.config = { ...this.config, ...newConfig };
        this.scheduleBackup(); // Reschedule backup with new configuration

        // Save configuration to file
        try {
            const configDir = path.join(process.cwd(), 'config');
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }

            fs.writeFileSync(
                path.join(configDir, 'backup.json'),
                JSON.stringify(this.config, null, 2)
            );

            this.logger.info('Backup configuration updated', { config: this.config });
        } catch (error) {
            this.logger.error('Failed to save backup configuration', { error: error as Error });
            throw error;
        }
    }

    public async verifyBackup(backupFileName: string): Promise<boolean> {
        const backupPath = path.join(this.config.backupDir, backupFileName);

        try {
            if (!fs.existsSync(backupPath)) {
                throw new Error(`Backup file not found: ${backupFileName}`);
            }

            // Verify backup file integrity
            const verifyCmd = `gzip -t ${backupPath}`;
            await execAsync(verifyCmd);

            this.logger.info('Backup verification successful', { backupFileName });
            return true;

        } catch (error) {
            this.logger.error('Backup verification failed', { error: error as Error, backupFileName });
            return false;
        }
    }

    public async shutdown(): Promise<void> {
        if (this.backupScheduler) {
            clearInterval(this.backupScheduler);
            this.backupScheduler = null;
        }

        this.logger.info('Backup Manager shutdown complete');
    }
}