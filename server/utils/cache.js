import NodeCache from 'node-cache';
import { Logger } from './logger';
export class CacheManager {
    static instance;
    cache;
    logger;
    constructor() {
        this.cache = new NodeCache({
            stdTTL: 0,
            checkperiod: 600,
            useClones: true
        });
        this.logger = Logger.getInstance('CacheManager');
    }
    static getInstance() {
        if (!CacheManager.instance) {
            CacheManager.instance = new CacheManager();
        }
        return CacheManager.instance;
    }
    set(key, value, ttl = 0) {
        try {
            const success = this.cache.set(key, value, ttl);
            if (!success) {
                this.logger.error('Failed to set cache', { error: new Error('Cache set operation failed'), key });
            }
            return success;
        }
        catch (error) {
            this.logger.error('Error setting cache', { error: error, key });
            return false;
        }
    }
    get(key) {
        try {
            return this.cache.get(key);
        }
        catch (error) {
            this.logger.error('Error getting cache', { error: error, key });
            return undefined;
        }
    }
    delete(key) {
        try {
            return this.cache.del(key);
        }
        catch (error) {
            this.logger.error('Error deleting cache', { error: error, key });
            return 0;
        }
    }
    flush() {
        try {
            this.cache.flushAll();
        }
        catch (error) {
            this.logger.error('Error flushing cache', { error: error });
        }
    }
    mget(keys) {
        try {
            return this.cache.mget(keys);
        }
        catch (error) {
            this.logger.error('Error getting multiple cache keys', { error: error, keys });
            return {};
        }
    }
    mset(keyValuePairs) {
        try {
            const data = keyValuePairs.map(({ key, val, ttl }) => ({
                key,
                val,
                ttl: ttl || 0
            }));
            return this.cache.mset(data);
        }
        catch (error) {
            this.logger.error('Error setting multiple cache keys', { error: error });
            return false;
        }
    }
    getOrSet(key, getValue, ttl = 0) {
        return new Promise(async (resolve, reject) => {
            try {
                const cachedValue = this.get(key);
                if (cachedValue !== undefined) {
                    return resolve(cachedValue);
                }
                const value = await getValue();
                const success = this.set(key, value, ttl);
                if (!success) {
                    this.logger.warn('Failed to cache computed value', { key });
                }
                resolve(value);
            }
            catch (error) {
                this.logger.error('Error in getOrSet operation', { error: error, key });
                reject(error);
            }
        });
    }
}
export default CacheManager;
