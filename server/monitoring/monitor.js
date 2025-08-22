import os from 'os';
import { EventEmitter } from 'events';
import { Logger } from '../utils/logger';
import { CacheManager } from '../utils/cache';
export class SystemMonitor extends EventEmitter {
    static instance;
    logger;
    cache;
    metricsInterval = null;
    alertThresholds = {
        cpuUsage: 80, // 80% CPU usage
        memoryUsage: 85, // 85% memory usage
        diskUsage: 90, // 90% disk usage
        scanDuration: 300000, // 5 minutes scan duration
        errorRate: 10 // 10% error rate
    };
    constructor() {
        super();
        this.logger = Logger.getInstance('SystemMonitor');
        this.cache = CacheManager.getInstance();
    }
    static getInstance() {
        if (!SystemMonitor.instance) {
            SystemMonitor.instance = new SystemMonitor();
        }
        return SystemMonitor.instance;
    }
    start(interval = 60000) {
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
            }
            catch (error) {
                this.logger.error('Error collecting metrics', { error });
            }
        }, interval);
        this.logger.info('System monitoring started', { interval });
    }
    stop() {
        if (this.metricsInterval) {
            clearInterval(this.metricsInterval);
            this.metricsInterval = null;
            this.logger.info('System monitoring stopped');
        }
    }
    setAlertThresholds(thresholds) {
        this.alertThresholds = { ...this.alertThresholds, ...thresholds };
        this.logger.info('Alert thresholds updated', { thresholds: this.alertThresholds });
    }
    async collectMetrics() {
        const cpus = os.cpus();
        const totalMemory = os.totalmem();
        const freeMemory = os.freemem();
        const usedMemory = totalMemory - freeMemory;
        // Get disk usage using node-disk-info (you'll need to install this package)
        const diskUsage = await this.getDiskUsage();
        // Get network connections count
        const networkConnections = await this.getNetworkConnections();
        const metrics = {
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
    analyzeMetrics(metrics) {
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
    emitAlert(type, data) {
        const alert = {
            type,
            timestamp: new Date().toISOString(),
            data
        };
        this.emit('alert', alert);
        this.logger.warn(`System Alert: ${type}`, data);
    }
    calculateCPUUsage(cpus) {
        const totalCPU = cpus.reduce((acc, cpu) => {
            const total = Object.values(cpu.times).reduce((a, b) => a + b);
            const idle = cpu.times.idle;
            return acc + ((total - idle) / total) * 100;
        }, 0);
        return totalCPU / cpus.length;
    }
    async getDiskUsage() {
        // This is a placeholder. In a real implementation, you would use
        // a package like 'node-disk-info' or 'diskusage'
        return {
            total: 0,
            used: 0,
            free: 0,
            percentUsed: 0
        };
    }
    async getNetworkConnections() {
        // This is a placeholder. In a real implementation, you would use
        // netstat or similar to get actual connection count
        return 0;
    }
    async getMetrics() {
        return this.cache.get('system_metrics') || null;
    }
    onAlert(callback) {
        this.on('alert', callback);
    }
    onMetrics(callback) {
        this.on('metrics', callback);
    }
}
