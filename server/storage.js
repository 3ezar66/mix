import { drizzle } from 'drizzle-orm/better-sqlite3';
import { sql } from 'drizzle-orm';
import connectSqlite3 from 'connect-sqlite3';
import session from 'express-session';
import 'dotenv/config';
import { detectedMiners, networkConnections, scanSessions, systemActivities, users, rfSignals, plcAnalysis, acousticSignatures, thermalSignatures, networkTraffic } from "@shared/schema";
// @ts-ignore
// Initialize database
const sqlite = new sqlite3.Database('ilam_mining.db');
const db = drizzle(sqlite);
export class DatabaseStorage {
    sessionStore;
    constructor() {
        const SQLiteStore = connectSqlite3(session);
        this.sessionStore = new SQLiteStore({
            table: 'sessions',
            db: 'sessions.db',
            dir: './data'
        });
    }
    async getUser(id) {
        return db.select().from(users).where(sql `${users.id} = ${id}`).get();
    }
    async getUserByUsername(username) {
        return db.select().from(users).where(sql `${users.username} = ${username}`).get();
    }
    async createUser(insertUser) {
        const result = db.insert(users).values(insertUser).run();
        const user = db.select()
            .from(users)
            .where(sql `${users.id} = ${result.lastInsertRowid}`)
            .get();
        if (!user) {
            throw new Error('Failed to create user');
        }
        return user;
    }
    async getDetectedMiners() {
        return db.select().from(detectedMiners).all();
    }
    async getMinerById(id) {
        return db.select().from(detectedMiners).where(sql `${detectedMiners.id} = ${id}`).get();
    }
    async createMiner(miner) {
        const result = db.insert(detectedMiners).values(miner).run();
        const insertedMiner = db.select()
            .from(detectedMiners)
            .where(sql `${detectedMiners.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedMiner) {
            throw new Error('Failed to create miner');
        }
        return insertedMiner;
    }
    async updateMiner(id, updates) {
        db.update(detectedMiners).set(updates).where(sql `${detectedMiners.id} = ${id}`).run();
        return this.getMinerById(id);
    }
    async getActiveMiners() {
        return db.select().from(detectedMiners).where(sql `${detectedMiners.status} = 'active'`).all();
    }
    async getMinersInArea(bounds) {
        return db.select().from(detectedMiners)
            .where(sql `${detectedMiners.latitude} <= ${bounds.north} AND ${detectedMiners.latitude} >= ${bounds.south} AND ${detectedMiners.longitude} <= ${bounds.east} AND ${detectedMiners.longitude} >= ${bounds.west}`).all();
    }
    async getNetworkConnections() {
        return db.select().from(networkConnections).all();
    }
    async createConnection(connection) {
        const result = db.insert(networkConnections).values(connection).run();
        const insertedConnection = db.select()
            .from(networkConnections)
            .where(sql `${networkConnections.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedConnection) {
            throw new Error('Failed to create connection');
        }
        return insertedConnection;
    }
    async getConnectionsByMiner(minerId) {
        return db.select().from(networkConnections).where(sql `${networkConnections.minerId} = ${minerId}`).all();
    }
    async getScanSessions() {
        return db.select().from(scanSessions).all();
    }
    async createScanSession(session) {
        const result = db.insert(scanSessions).values(session).run();
        const insertedSession = db.select()
            .from(scanSessions)
            .where(sql `${scanSessions.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedSession) {
            throw new Error('Failed to create scan session');
        }
        return insertedSession;
    }
    async updateScanSession(id, updates) {
        db.update(scanSessions).set(updates).where(sql `${scanSessions.id} = ${id}`).run();
        return db.select().from(scanSessions).where(sql `${scanSessions.id} = ${id}`).get();
    }
    async getActiveScanSessions() {
        return db.select().from(scanSessions).where(sql `${scanSessions.status} = 'active'`).all();
    }
    async getRecentActivities(limit = 100) {
        return db.select().from(systemActivities).orderBy(sql `${systemActivities.timestamp} DESC`).limit(limit).all();
    }
    async createActivity(activity) {
        const result = db.insert(systemActivities).values(activity).run();
        const insertedActivity = db.select()
            .from(systemActivities)
            .where(sql `${systemActivities.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedActivity) {
            throw new Error('Failed to create activity');
        }
        return insertedActivity;
    }
    async getRfSignals() {
        return db.select().from(rfSignals).all();
    }
    async createRfSignal(signal) {
        const result = db.insert(rfSignals).values(signal).run();
        const insertedSignal = db.select()
            .from(rfSignals)
            .where(sql `${rfSignals.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedSignal) {
            throw new Error('Failed to create RF signal');
        }
        return insertedSignal;
    }
    async getRfSignalsByLocation(location) {
        return db.select().from(rfSignals).where(sql `${rfSignals.location} = ${location}`).all();
    }
    async getPlcAnalyses() {
        return db.select().from(plcAnalysis).all();
    }
    async createPlcAnalysis(analysis) {
        const result = db.insert(plcAnalysis).values(analysis).run();
        const insertedAnalysis = db.select()
            .from(plcAnalysis)
            .where(sql `${plcAnalysis.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedAnalysis) {
            throw new Error('Failed to create PLC analysis');
        }
        return insertedAnalysis;
    }
    async getAcousticSignatures() {
        return db.select().from(acousticSignatures).all();
    }
    async createAcousticSignature(signature) {
        const result = db.insert(acousticSignatures).values(signature).run();
        const insertedSignature = db.select()
            .from(acousticSignatures)
            .where(sql `${acousticSignatures.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedSignature) {
            throw new Error('Failed to create acoustic signature');
        }
        return insertedSignature;
    }
    async getThermalSignatures() {
        return db.select().from(thermalSignatures).all();
    }
    async createThermalSignature(signature) {
        const result = db.insert(thermalSignatures).values(signature).run();
        const insertedSignature = db.select()
            .from(thermalSignatures)
            .where(sql `${thermalSignatures.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedSignature) {
            throw new Error('Failed to create thermal signature');
        }
        return insertedSignature;
    }
    async getNetworkTraffic() {
        return db.select().from(networkTraffic).all();
    }
    async createNetworkTraffic(traffic) {
        const result = db.insert(networkTraffic).values(traffic).run();
        const insertedTraffic = db.select()
            .from(networkTraffic)
            .where(sql `${networkTraffic.id} = ${result.lastInsertRowid}`)
            .get();
        if (!insertedTraffic) {
            throw new Error('Failed to create network traffic');
        }
        return insertedTraffic;
    }
    async getStratumConnections() {
        return db.select().from(networkTraffic).where(sql `${networkTraffic.protocol} = 'stratum'`).all();
    }
    async getStatistics() {
        const totalDevices = db.select().from(detectedMiners).all().length;
        const confirmedMiners = db.select().from(detectedMiners).where(sql `${detectedMiners.status} = 'confirmed'`).all().length;
        const suspiciousDevices = db.select().from(detectedMiners).where(sql `${detectedMiners.status} = 'suspicious'`).all().length;
        const rfSignalsDetected = db.select().from(rfSignals).all().length;
        const acousticSignaturesCount = db.select().from(acousticSignatures).all().length;
        const thermalAnomalies = db.select().from(thermalSignatures).all().length;
        return {
            totalDevices,
            confirmedMiners,
            suspiciousDevices,
            totalPowerConsumption: 0, // Placeholder
            networkHealth: 100, // Placeholder
            rfSignalsDetected,
            acousticSignatures: acousticSignaturesCount,
            thermalAnomalies
        };
    }
}
// Utility functions
export function getStatistics() {
    const storage = new DatabaseStorage();
    return storage.getStatistics();
}
export function getMiners() {
    const storage = new DatabaseStorage();
    return storage.getDetectedMiners();
}
export function getActivities() {
    const storage = new DatabaseStorage();
    return storage.getRecentActivities();
}
function isValidIP(ip) {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipRegex.test(ip);
}
function isValidPort(port) {
    return port >= 1 && port <= 65535;
}
function isValidOpenPorts(open_ports) {
    try {
        const ports = JSON.parse(open_ports);
        return Array.isArray(ports) && ports.every(isValidPort);
    }
    catch {
        return false;
    }
}
export function addMiner(miner) {
    if (!isValidIP(miner.ip)) {
        throw new Error('Invalid IP address');
    }
    if (miner.open_ports && !isValidOpenPorts(miner.open_ports)) {
        throw new Error('Invalid open ports format');
    }
    const storage = new DatabaseStorage();
    return storage.createMiner(miner);
}
export function addActivity(activity) {
    const storage = new DatabaseStorage();
    return storage.createActivity(activity);
}
// Memory storage for testing
export class MemStorage {
    sessionStore;
    async getUser(id) {
        return undefined;
    }
    async getUserByUsername(username) {
        return undefined;
    }
    async createUser(user) {
        throw new Error('Not implemented');
    }
    async getDetectedMiners() {
        return [];
    }
    async getMinerById(id) {
        return undefined;
    }
    async createMiner(miner) {
        throw new Error('Not implemented');
    }
    async updateMiner(id, updates) {
        return undefined;
    }
    async getActiveMiners() {
        return [];
    }
    async getMinersInArea(bounds) {
        return [];
    }
    async getNetworkConnections() {
        return [];
    }
    async createConnection(connection) {
        throw new Error('Not implemented');
    }
    async getConnectionsByMiner(minerId) {
        return [];
    }
    async getScanSessions() {
        return [];
    }
    async createScanSession(session) {
        throw new Error('Not implemented');
    }
    async updateScanSession(id, updates) {
        return undefined;
    }
    async getActiveScanSessions() {
        return [];
    }
    async getRecentActivities(limit) {
        return [];
    }
    async createActivity(activity) {
        throw new Error('Not implemented');
    }
    async getRfSignals() {
        return [];
    }
    async createRfSignal(signal) {
        throw new Error('Not implemented');
    }
    async getRfSignalsByLocation(location) {
        return [];
    }
    async getPlcAnalyses() {
        return [];
    }
    async createPlcAnalysis(analysis) {
        throw new Error('Not implemented');
    }
    async getAcousticSignatures() {
        return [];
    }
    async createAcousticSignature(signature) {
        throw new Error('Not implemented');
    }
    async getThermalSignatures() {
        return [];
    }
    async createThermalSignature(signature) {
        throw new Error('Not implemented');
    }
    async getNetworkTraffic() {
        return [];
    }
    async createNetworkTraffic(traffic) {
        throw new Error('Not implemented');
    }
    async getStratumConnections() {
        return [];
    }
    async getStatistics() {
        return {
            totalDevices: 0,
            confirmedMiners: 0,
            suspiciousDevices: 0,
            totalPowerConsumption: 0,
            networkHealth: 0,
            rfSignalsDetected: 0,
            acousticSignatures: 0,
            thermalAnomalies: 0
        };
    }
}
