import NodeCache from 'node-cache';
import { Logger } from './logger';

export class CacheManager {
    private static instance: CacheManager;
    private cache: NodeCache;
    private logger: Logger;

    private constructor() {
        this.cache = new NodeCache({
            stdTTL: 0,
            checkperiod: 600,
            useClones: true
        });
        this.logger = Logger.getInstance('CacheManager');
    }

    public static getInstance(): CacheManager {
        if (!CacheManager.instance) {
            CacheManager.instance = new CacheManager();
        }
        return CacheManager.instance;
    }

    public set(key: string | number, value: any, ttl: number = 0): boolean {
        try {
            const success = this.cache.set(key, value, ttl);
            if (!success) {
                this.logger.error('Failed to set cache', { error: new Error('Cache set operation failed'), key });
            }
            return success;
        } catch (error) {
            this.logger.error('Error setting cache', { error: error as Error, key });
            return false;
        }
    }

    public get<T>(key: string | number): T | undefined {
        try {
            return this.cache.get<T>(key);
        } catch (error) {
            this.logger.error('Error getting cache', { error: error as Error, key });
            return undefined;
        }
    }

    public delete(key: string | number): number {
        try {
            return this.cache.del(key);
        } catch (error) {
            this.logger.error('Error deleting cache', { error: error as Error, key });
            return 0;
        }
    }

    public flush(): void {
        try {
            this.cache.flushAll();
        } catch (error) {
            this.logger.error('Error flushing cache', { error: error as Error });
        }
    }

    public mget<T>(keys: (string | number)[]): { [key: string]: T } {
        try {
            return this.cache.mget<T>(keys);
        } catch (error) {
            this.logger.error('Error getting multiple cache keys', { error: error as Error, keys });
            return {};
        }
    }

    public mset(keyValuePairs: { key: string | number; val: any; ttl?: number }[]): boolean {
        try {
            const data = keyValuePairs.map(({ key, val, ttl }) => ({
                key,
                val,
                ttl: ttl || 0
            }));
            return this.cache.mset(data);
        } catch (error) {
            this.logger.error('Error setting multiple cache keys', { error: error as Error });
            return false;
        }
    }

    public getOrSet<T>(key: string | number, getValue: () => Promise<T>, ttl: number = 0): Promise<T> {
        return new Promise<T>(async (resolve, reject) => {
            try {
                const cachedValue = this.get<T>(key);
                if (cachedValue !== undefined) {
                    return resolve(cachedValue);
                }

                const value = await getValue();
                const success = this.set(key, value, ttl);
                if (!success) {
                    this.logger.warn('Failed to cache computed value', { key });
                }
                resolve(value);
            } catch (error) {
                this.logger.error('Error in getOrSet operation', { error: error as Error, key });
                reject(error);
            }
        });
    }
}

export default CacheManager;