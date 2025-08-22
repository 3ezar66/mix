import * as net from 'net';
import { exec } from 'child_process';
import { promisify } from 'util';
import { Logger } from '../utils/logger';
const execAsync = promisify(exec);
export class NetworkScanner {
    MINING_PORTS = [
        3333, 3334, 3335, // Stratum
        8332, 8333, // Bitcoin
        4444, 4445, // Ethereum
        7777, 7778, // Various mining pools
        9332, 9333 // Various mining pools
    ];
    SUSPICIOUS_IPS = new Set();
    logger;
    constructor() {
        this.logger = Logger.getInstance('NetworkScanner');
        this.loadSuspiciousIPs();
    }
    async loadSuspiciousIPs() {
        try {
            // بارگذاری لیست IP های مشکوک از فایل یا API
            const response = await fetch('https://api.mining-pools.io/suspicious-ips');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            data.ips.forEach((ip) => this.SUSPICIOUS_IPS.add(ip));
        }
        catch (error) {
            this.logger.error('Failed to load suspicious IPs', { error: error });
        }
    }
    async scanDevice(ipAddress) {
        try {
            const [portScan, bandwidthUsage, connections] = await Promise.all([
                this.scanPorts(ipAddress),
                this.checkBandwidthUsage(ipAddress),
                this.checkConnections(ipAddress)
            ]);
            return {
                miningPortsDetected: this.calculatePortScore(portScan),
                highBandwidthUsage: bandwidthUsage,
                suspiciousConnections: connections
            };
        }
        catch (error) {
            this.logger.error(`Error scanning device ${ipAddress}`, { error: error });
            throw error;
        }
    }
    async scanPorts(ip) {
        const openPorts = [];
        await Promise.all(this.MINING_PORTS.map(async (port) => {
            try {
                await this.checkPort(ip, port);
                openPorts.push(port);
            }
            catch (error) {
                // Port is closed or unreachable
            }
        }));
        return openPorts;
    }
    checkPort(ip, port) {
        return new Promise((resolve, reject) => {
            const socket = new net.Socket();
            socket.setTimeout(1000);
            socket.on('connect', () => {
                socket.destroy();
                resolve();
            });
            socket.on('error', (err) => {
                socket.destroy();
                reject(err);
            });
            socket.on('timeout', () => {
                socket.destroy();
                reject(new Error('timeout'));
            });
            socket.connect(port, ip);
        });
    }
    async checkBandwidthUsage(ip) {
        try {
            // استفاده از ابزار iftop یا nethogs برای بررسی مصرف پهنای باند
            const { stdout } = await execAsync(`nethogs -t -c 5 | grep ${ip}`);
            const usage = this.parseBandwidthUsage(stdout);
            return this.normalizeBandwidthUsage(usage);
        }
        catch (error) {
            this.logger.error('Error checking bandwidth usage', { error: error });
            return 0;
        }
    }
    async checkConnections(ip) {
        try {
            const { stdout } = await execAsync(`netstat -n | grep ${ip}`);
            const connections = stdout.split('\n').filter(line => line.trim());
            const suspiciousCount = connections.filter(conn => {
                const remoteIP = conn.split(/\s+/)[5]?.split(':')[0];
                return remoteIP && this.SUSPICIOUS_IPS.has(remoteIP);
            }).length;
            return Math.min(1, suspiciousCount / connections.length);
        }
        catch (error) {
            this.logger.error('Error checking connections', { error: error });
            return 0;
        }
    }
    calculatePortScore(openPorts) {
        // محاسبه امتیاز بر اساس تعداد پورت‌های باز مرتبط با ماینینگ
        return Math.min(5, openPorts.length);
    }
    parseBandwidthUsage(stdout) {
        // پردازش خروجی nethogs و استخراج میزان مصرف پهنای باند
        const lines = stdout.split('\n');
        let totalUsage = 0;
        for (const line of lines) {
            const match = line.match(/(\d+\.?\d*)\s*(KB|MB|GB)\/s/);
            if (match) {
                const [, value, unit] = match;
                totalUsage += this.convertToMBps(parseFloat(value), unit);
            }
        }
        return totalUsage;
    }
    convertToMBps(value, unit) {
        switch (unit) {
            case 'KB': return value / 1024;
            case 'GB': return value * 1024;
            default: return value;
        }
    }
    normalizeBandwidthUsage(mbps) {
        // نرمال‌سازی مصرف پهنای باند (فرض: بیش از 100Mbps مشکوک است)
        return Math.min(1, mbps / 100);
    }
}
