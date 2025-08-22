import * as winston from 'winston';
import 'winston-daily-rotate-file';
export class Logger {
    logger;
    static instance;
    maxLogSize = 20 * 1024 * 1024; // 20MB
    constructor(serviceName) {
        this.logger = winston.createLogger({
            level: 'info',
            format: winston.format.combine(winston.format.timestamp(), winston.format.errors({ stack: true }), winston.format.json()),
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
                // لاگ‌های امنیتی
                new winston.transports.DailyRotateFile({
                    filename: 'logs/security-%DATE%.log',
                    datePattern: 'YYYY-MM-DD',
                    maxSize: '20m',
                    maxFiles: '30d',
                    format: winston.format.combine(winston.format.timestamp(), winston.format.json())
                })
            ]
        });
        // در محیط development، نمایش لاگ‌ها در کنسول
        if (process.env.NODE_ENV !== 'production') {
            this.logger.add(new winston.transports.Console({
                format: winston.format.combine(winston.format.colorize(), winston.format.simple())
            }));
        }
    }
    static getInstance(serviceName) {
        if (!Logger.instance) {
            Logger.instance = new Logger(serviceName);
        }
        return Logger.instance;
    }
    error(message, meta) {
        const enrichedMeta = this.enrichMetadata(meta);
        if (meta?.error instanceof Error) {
            enrichedMeta.stack = meta.error.stack;
        }
        this.logger.error(message, enrichedMeta);
    }
    warn(message, meta) {
        this.logger.warn(message, this.enrichMetadata(meta));
    }
    info(message, meta) {
        this.logger.info(message, this.enrichMetadata(meta));
    }
    debug(message, meta) {
        this.logger.debug(message, this.enrichMetadata(meta));
    }
    security(message, meta) {
        const enrichedMeta = this.enrichMetadata(meta);
        this.logger.log({
            level: 'info',
            message,
            ...enrichedMeta,
            security: true,
            timestamp: new Date().toISOString()
        });
    }
    performance(operation, duration, meta) {
        this.info(`Performance: ${operation} completed in ${duration}ms`, {
            ...meta,
            duration,
            type: 'performance'
        });
    }
    audit(action, meta) {
        this.info(`Audit: ${action}`, {
            ...meta,
            type: 'audit',
            timestamp: new Date().toISOString()
        });
    }
    enrichMetadata(meta) {
        return {
            ...meta,
            hostname: require('os').hostname(),
            pid: process.pid,
            timestamp: new Date().toISOString()
        };
    }
    async rotateLogs() {
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
        }
        catch (error) {
            this.error('Error rotating logs', { error: error });
        }
    }
}
