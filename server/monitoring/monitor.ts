import os from 'os';
import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { CacheManager } from '../utils/cache';

interface SystemMetrics {
    cpuUsage: number;
    memoryUsage: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
    };
    diskUsage: {
        total: number;
        used: number;
        free: number;
        percentUsed: number;
    };
    networkConnections: number;
    uptime: number;
}

interface AlertThresholds {
    cpuUsage: number;
    memoryUsage: number;
    diskUsage: number;
    scanDuration: number;
    errorRate: number;
}

export class SystemMonitor extends EventEmitter {
    private static instance: SystemMonitor;
    private logger: Logger;
    private cache: CacheManager;
    private metricsInterval: NodeJS.Timeout | null = null;
    private alertThresholds: AlertThresholds = {
        cpuUsage: 80,         // 80% CPU usage
        memoryUsage: 85,      // 85% memory usage
        diskUsage: 90,        // 90% disk usage
        scanDuration: 300000, // 5 minutes scan duration
        errorRate: 10         // 10% error rate
    };

    private constructor() {
        super();
        this.logger = Logger.getInstance('SystemMonitor');
        this.cache = CacheManager.getInstance();
    }

    public static getInstance(): SystemMonitor {
        if (!SystemMonitor.instance) {
            SystemMonitor.instance = new SystemMonitor();
        }
        return SystemMonitor.instance;
    }

    public start(interval: number = 60000): void {
        if (this.metricsInterval) {
            this.logger.warn('Monitor already running');
            return;
        }

        this.metricsInterval = setInterval(async () => {
            try {
                const metrics = await this.collectMetrics();
                this.analyzeMetrics(metrics);
                this.cache.set('system_metrics', metrics);
                this.emit('metrics', metrics);
            } catch (error) {
                this.logger.error('Error collecting metrics', { error });
            }
        }, interval);

        this.logger.info('System monitoring started', { interval });
    }

    public stop(): void {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
            this.logger.info('System monitoring stopped');
        }
    }

    public setAlertThresholds(thresholds: Partial<AlertThresholds>): void {
        this.alertThresholds = { ...this.alertThresholds, ...thresholds };
        this.logger.info('Alert thresholds updated', { thresholds: this.alertThresholds });
    }

    private async collectMetrics(): Promise<SystemMetrics> {
        const cpus = os.cpus();
        const totalMemory = os.totalmem();
        const freeMemory = os.freemem();
        const usedMemory = totalMemory - freeMemory;

        // Get disk usage using node-disk-info (you'll need to install this package)
        const diskUsage = await this.getDiskUsage();

        // Get network connections count
        const networkConnections = await this.getNetworkConnections();

        const metrics: SystemMetrics = {
            cpuUsage: this.calculateCPUUsage(cpus),
            memoryUsage: {
                total: totalMemory,
                used: usedMemory,
                free: freeMemory,
                percentUsed: (usedMemory / totalMemory) * 100
            },
            diskUsage,
            networkConnections,
            uptime: os.uptime()
        };

        return metrics;
    }

    private analyzeMetrics(metrics: SystemMetrics): void {
        // CPU Usage Alert
        if (metrics.cpuUsage > this.alertThresholds.cpuUsage) {
            this.emitAlert('HIGH_CPU_USAGE', {
                current: metrics.cpuUsage,
                threshold: this.alertThresholds.cpuUsage
            });
        }

        // Memory Usage Alert
        if (metrics.memoryUsage.percentUsed > this.alertThresholds.memoryUsage) {
            this.emitAlert('HIGH_MEMORY_USAGE', {
                current: metrics.memoryUsage.percentUsed,
                threshold: this.alertThresholds.memoryUsage
            });
        }

        // Disk Usage Alert
        if (metrics.diskUsage.percentUsed > this.alertThresholds.diskUsage) {
            this.emitAlert('HIGH_DISK_USAGE', {
                current: metrics.diskUsage.percentUsed,
                threshold: this.alertThresholds.diskUsage
            });
        }
    }

    private emitAlert(type: string, data: any): void {
        const alert = {
            type,
            timestamp: new Date().toISOString(),
            data
        };

        this.emit('alert', alert);
        this.logger.warn(`System Alert: ${type}`, data);
    }

    private calculateCPUUsage(cpus: os.CpuInfo[]): number {
        const totalCPU = cpus.reduce((acc, cpu) => {
            const total = Object.values(cpu.times).reduce((a, b) => a + b);
            const idle = cpu.times.idle;
            return acc + ((total - idle) / total) * 100;
        }, 0);

        return totalCPU / cpus.length;
    }

    private async getDiskUsage(): Promise<SystemMetrics['diskUsage']> {
        // This is a placeholder. In a real implementation, you would use
        // a package like 'node-disk-info' or 'diskusage'
        return {
            total: 0,
            used: 0,
            free: 0,
            percentUsed: 0
        };
    }

    private async getNetworkConnections(): Promise<number> {
        // This is a placeholder. In a real implementation, you would use
        // netstat or similar to get actual connection count
        return 0;
    }

    public async getMetrics(): Promise<SystemMetrics | null> {
        return this.cache.get<SystemMetrics>('system_metrics') || null;
    }

    public onAlert(callback: (alert: any) => void): void {
        this.on('alert', callback);
    }

    public onMetrics(callback: (metrics: SystemMetrics) => void): void {
        this.on('metrics', callback);
    }
}