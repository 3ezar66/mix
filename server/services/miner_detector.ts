import { Logger } from '../utils/logger';
import { CacheManager } from '../utils/cache';
import * as os from 'os';
import * as ps from 'ps-node';

interface ProcessInfo {
    pid: number;
    name: string;
    cpu: number;
    memory: number;
    networkConnections?: string[];
}

interface SystemMetrics {
    cpuUsage: number;
    memoryUsage: number;
}

export class MinerDetector {
    private logger: Logger;
    private cache: CacheManager;

    constructor() {
        this.logger = Logger.getInstance('MinerDetector');
        this.cache = CacheManager.getInstance();
    }

    private readonly knownMiners: string[] = [
        'xmrig', 'ethminer', 'cgminer', 'bfgminer',
        'ccminer', 'nheqminer', 'excavator', 'nbminer',
        'phoenixminer', 'teamredminer', 'gminer', 'trex'
    ];

    public async detectByProcessName(): Promise<ProcessInfo[]> {
        try {
            const cachedProcesses = await this.cache.get('miner_processes');
            if (cachedProcesses) {
                return cachedProcesses as ProcessInfo[];
            }

            const suspiciousProcesses: ProcessInfo[] = [];
            const processes = await this.getRunningProcesses();

            for (const process of processes) {
                const processName = process.name.toLowerCase();
                if (this.knownMiners.some(miner => processName.includes(miner))) {
                    const processInfo: ProcessInfo = {
                        pid: process.pid,
                        name: process.name,
                        cpu: await this.getProcessCPUUsage(process.pid),
                        memory: await this.getProcessMemoryUsage(process.pid),
                        networkConnections: await this.getProcessNetworkConnections(process.pid)
                    };
                    suspiciousProcesses.push(processInfo);
                }
            }

            await this.cache.set('miner_processes', suspiciousProcesses);
            return suspiciousProcesses;
        } catch (error) {
            this.logger.error('Error detecting mining processes by name', { error });
            throw error;
        }
    }

    public async detectByHighCPU(threshold: number = 90): Promise<ProcessInfo[]> {
        try {
            const processes = await this.getRunningProcesses();
            const highCPUProcesses: ProcessInfo[] = [];

            for (const process of processes) {
                const cpuUsage = await this.getProcessCPUUsage(process.pid);
                if (cpuUsage > threshold) {
                    const processInfo: ProcessInfo = {
                        pid: process.pid,
                        name: process.name,
                        cpu: cpuUsage,
                        memory: await this.getProcessMemoryUsage(process.pid),
                        networkConnections: await this.getProcessNetworkConnections(process.pid)
                    };
                    highCPUProcesses.push(processInfo);
                }
            }

            return highCPUProcesses;
        } catch (error) {
            this.logger.error('Error detecting high CPU processes', { error });
            throw error;
        }
    }

    public async getSystemMetrics(): Promise<SystemMetrics> {
        const cpus = os.cpus();
        const totalMemory = os.totalmem();
        const freeMemory = os.freemem();

        const cpuUsage = cpus.reduce((acc, cpu) => {
            const total = Object.values(cpu.times).reduce((a, b) => a + b);
            const idle = cpu.times.idle;
            return acc + ((total - idle) / total) * 100;
        }, 0) / cpus.length;

        const memoryUsage = ((totalMemory - freeMemory) / totalMemory) * 100;

        return {
            cpuUsage: Math.round(cpuUsage),
            memoryUsage: Math.round(memoryUsage)
        };
    }

    private getRunningProcesses(): Promise<{ pid: number; name: string }[]> {
        return new Promise((resolve, reject) => {
            ps.lookup({}, (error: Error | null, processes: any[]) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve(processes.map(process => ({
                    pid: parseInt(process.pid),
                    name: process.command || ''
                })));
            });
        });
    }

    private async getProcessCPUUsage(pid: number): Promise<number> {
        // Implementation depends on the OS and available metrics
        // This is a simplified version
        return new Promise((resolve) => {
            ps.lookup({ pid: pid }, (error: Error | null, processes: any[]) => {
                if (error || !processes.length) {
                    resolve(0);
                    return;
                }
                // This is a mock value, real implementation would need to calculate actual CPU usage
                resolve(Math.random() * 100);
            });
        });
    }

    private async getProcessMemoryUsage(pid: number): Promise<number> {
        return new Promise((resolve) => {
            ps.lookup({ pid: pid }, (error: Error | null, processes: any[]) => {
                if (error || !processes.length) {
                    resolve(0);
                    return;
                }
                // This is a mock value, real implementation would need to get actual memory usage
                resolve(Math.random() * 1000);
            });
        });
    }

    private async getProcessNetworkConnections(pid: number): Promise<string[]> {
        // Implementation would need to use netstat or similar tools
        // This is a mock implementation
        return [];
    }
}