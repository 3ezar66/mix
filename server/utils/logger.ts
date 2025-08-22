import * as winston from 'winston';
import 'winston-daily-rotate-file';

interface LogMetadata {
    service?: string;
    context?: string;
    userId?: string;
    ip?: string;
    duration?: number;
    error?: Error | unknown;
    [key: string]: any;
}

export class Logger {
    private logger: winston.Logger;
    private static _instance: Logger;
    private readonly maxLogSize = 20 * 1024 * 1024; // 20MB

    private constructor(serviceName: string) {
        this.logger = winston.createLogger({
            level: 'info',
            format: winston.format.combine(
                winston.format.timestamp(),
                winston.format.errors({ stack: true }),
                winston.format.json()
            ),
            defaultMeta: { service: serviceName },
            transports: [
                // لاگ‌های مهم در فایل جداگانه
                new winston.transports.DailyRotateFile({
                    filename: 'logs/error-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    level: 'error',
                    maxSize: '20m',
                    maxFiles: '14d'
                }),
                // همه لاگ‌ها
                new winston.transports.DailyRotateFile({
                    filename: 'logs/combined-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    maxSize: '20m',
                    maxFiles: '14d'
                }),
            ]
        });
    }

    public static getInstance(serviceName: string = 'default'): Logger {
        if (!Logger._instance) {
            Logger._instance = new Logger(serviceName);
        }
        return Logger._instance;
    }

    error(message: string, meta?: LogMetadata) {
        const enrichedMeta = this.enrichMetadata(meta);
        if (meta?.error instanceof Error) {
            enrichedMeta.stack = meta.error.stack;
        }
        this.logger.error(message, enrichedMeta);
    }

    warn(message: string, meta?: LogMetadata) {
        this.logger.warn(message, this.enrichMetadata(meta));
    }

    info(message: string, meta?: LogMetadata) {
        this.logger.info(message, this.enrichMetadata(meta));
    }

    debug(message: string, meta?: LogMetadata) {
        this.logger.debug(message, this.enrichMetadata(meta));
    }

    security(message: string, meta: LogMetadata) {
        const enrichedMeta = this.enrichMetadata(meta);
        this.logger.log({
            level: 'info',
            message,
            ...enrichedMeta,
            security: true,
            timestamp: new Date().toISOString()
        });
    }

    performance(operation: string, duration: number, meta?: LogMetadata) {
        this.info(`Performance: ${operation} completed in ${duration}ms`, {
            ...meta,
            duration,
            type: 'performance'
        });
    }

    audit(action: string, meta: LogMetadata) {
        this.info(`Audit: ${action}`, {
            ...meta,
            type: 'audit',
            timestamp: new Date().toISOString()
        });
    }

    private enrichMetadata(meta?: LogMetadata): LogMetadata {
        return {
            ...meta,
            hostname: require('os').hostname(),
            pid: process.pid,
            timestamp: new Date().toISOString()
        };
    }

    public async rotateLogs(): Promise<void> {
        const fs = require('fs').promises;
        const path = require('path');
        const logDir = 'logs';

        try {
            const files = await fs.readdir(logDir);
            for (const file of files) {
                const filePath = path.join(logDir, file);
                const stats = await fs.stat(filePath);

                if (stats.size > this.maxLogSize) {
                    const newPath = filePath + '.' + Date.now() + '.old';
                    await fs.rename(filePath, newPath);
                    this.info(`Rotated log file: ${file} to ${newPath}`);
                }
            }
        } catch (error) {
            this.error('Error rotating logs', { error: error as Error });
        }
    }
}
