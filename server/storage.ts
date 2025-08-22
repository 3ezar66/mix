import { Database } from 'better-sqlite3';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import { eq, and, desc } from 'drizzle-orm';
import { type SQLiteTable } from 'drizzle-orm/sqlite-core';

import connectSqlite3 from 'connect-sqlite3';
import session from 'express-session';

import {
  users,
  rfSignals,
  plcAnalysis,
  acousticSignatures,
  thermalSignatures,
  networkTraffic,
  miners,
  scanSessions,
  type User,
  type InsertUser,
  type RfSignal,
  type InsertRfSignal,
  type PlcAnalysis,
  type InsertPlcAnalysis,
  type AcousticSignature,
  type InsertAcousticSignature,
  type ThermalSignature,
  type InsertThermalSignature,
  type NetworkTraffic,
  type InsertNetworkTraffic,
  type Miner,
  type InsertMiner,
  type ScanSession,
  type InsertScanSession
} from "../shared/schema";

// Initialize database
const sqlite = new Database('ilam_mining.db');
const db = drizzle(sqlite);

export class DatabaseStorage implements IStorage {
  sessionStore: session.Store;

  constructor() {
    const SQLiteStore = connectSqlite3(session);
    this.sessionStore = new SQLiteStore({
      table: 'sessions',
      db: 'sessions.db',
      dir: './data'
    });
  }
  updateMiner(id: number, updates: Partial<InsertMiner>): Promise<DetectedMiner | undefined> {
    throw new Error('Method not implemented.');
  }
  getActiveMiners(): Promise<DetectedMiner[]> {
    throw new Error('Method not implemented.');
  }
  getMinersInArea(bounds: { north: number; south: number; east: number; west: number; }): Promise<DetectedMiner[]> {
    throw new Error('Method not implemented.');
  }
  getNetworkConnections(): Promise<NetworkConnection[]> {
    throw new Error('Method not implemented.');
  }
  createConnection(connection: InsertConnection): Promise<NetworkConnection> {
    throw new Error('Method not implemented.');
  }
  getConnectionsByMiner(minerId: number): Promise<NetworkConnection[]> {
    throw new Error('Method not implemented.');
  }
  getScanSessions(): Promise<ScanSession[]> {
    throw new Error('Method not implemented.');
  }
  createScanSession(session: InsertScanSession): Promise<ScanSession> {
    throw new Error('Method not implemented.');
  }
  updateScanSession(id: number, updates: Partial<InsertScanSession>): Promise<ScanSession | undefined> {
    throw new Error('Method not implemented.');
  }
  getActiveScanSessions(): Promise<ScanSession[]> {
    throw new Error('Method not implemented.');
  }
  getRecentActivities(limit?: number): Promise<SystemActivity[]> {
    throw new Error('Method not implemented.');
  }
  createActivity(activity: InsertActivity): Promise<SystemActivity> {
    throw new Error('Method not implemented.');
  }
  getRfSignals(): Promise<RfSignal[]> {
    throw new Error('Method not implemented.');
  }
  createRfSignal(signal: InsertRfSignal): Promise<RfSignal> {
    throw new Error('Method not implemented.');
  }
  getRfSignalsByLocation(location: string): Promise<RfSignal[]> {
    throw new Error('Method not implemented.');
  }
  getPlcAnalyses(): Promise<PlcAnalysis[]> {
    throw new Error('Method not implemented.');
  }
  createPlcAnalysis(analysis: InsertPlcAnalysis): Promise<PlcAnalysis> {
    throw new Error('Method not implemented.');
  }
  getAcousticSignatures(): Promise<AcousticSignature[]> {
    throw new Error('Method not implemented.');
  }
  createAcousticSignature(signature: InsertAcousticSignature): Promise<AcousticSignature> {
    throw new Error('Method not implemented.');
  }
  getThermalSignatures(): Promise<ThermalSignature[]> {
    throw new Error('Method not implemented.');
  }
  createThermalSignature(signature: InsertThermalSignature): Promise<ThermalSignature> {
    throw new Error('Method not implemented.');
  }
  getNetworkTraffic(): Promise<NetworkTraffic[]> {
    throw new Error('Method not implemented.');
  }
  createNetworkTraffic(traffic: InsertNetworkTraffic): Promise<NetworkTraffic> {
    throw new Error('Method not implemented.');
  }
  getStratumConnections(): Promise<NetworkTraffic[]> {
    throw new Error('Method not implemented.');
  }

  async getScanSessions(): Promise<ScanSession[]> {
    return db.select().from(scanSessions as unknown as SQLiteTable).all();
  }

  async createScanSession(session: InsertScanSession): Promise<ScanSession> {
    const result = db.insert(scanSessions as unknown as SQLiteTable).values(session).run();
    const createdSession = db.select()
      .from(scanSessions as unknown as SQLiteTable)
      .where(eq(scanSessions.id, result.lastInsertRowid as number))
      .get();
    if (!createdSession) {
      throw new Error('Failed to create scan session');
    }
    return createdSession;
  }

  async updateScanSession(id: number, updates: Partial<InsertScanSession>): Promise<ScanSession | undefined> {
    db.update(scanSessions as unknown as SQLiteTable)
      .set(updates)
      .where(eq(scanSessions.id, id))
      .run();
    return db.select()
      .from(scanSessions as unknown as SQLiteTable)
      .where(eq(scanSessions.id, id))
      .get();
  }

  async getActiveScanSessions(): Promise<ScanSession[]> {
    return db.select()
      .from(scanSessions as unknown as SQLiteTable)
      .where(eq(scanSessions.status, 'in_progress'))
      .all();
  }
  getStatistics(): Promise<{
    totalDevices: number;
    confirmedMiners: number;
    suspiciousDevices: number;
    totalPowerConsumption: number;
    networkHealth: number;
    rfSignalsDetected: number;
    acousticSignatures: number;
    thermalAnomalies: number;
  }> {
    throw new Error('Method not implemented.');
  }

  async getUser(id: number): Promise<User | undefined> {
    return db.select().from(users).where(eq(users.id, id)).get();
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return db.select().from(users).where(eq(users.username, username)).get();
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const result = db.insert(users).values(insertUser).run();
    const user = db.select()
      .from(users)
      .where(eq(users.id, result.lastInsertRowid as number))
      .get();
    if (!user) {
      throw new Error('Failed to create user');
    }
    return user;
  }

  async getDetectedMiners(): Promise<DetectedMiner[]> {
    return db.select().from(detectedMiners).all();
  }

  async getMinerById(id: number): Promise<DetectedMiner | undefined> {
    return db.select().from(detectedMiners).where(eq(detectedMiners.id, id)).get();
  }

  async createMiner(miner: InsertMiner): Promise<DetectedMiner> {
    const result = db.insert(detectedMiners).values(miner).run();
    const insertedMiner = db.select()
      .from(detectedMiners)
      .where(eq(detectedMiners.id, result.lastInsertRowid as number))
      .get();
    if (!insertedMiner) {
      throw new Error('Failed to create miner');
    }
    return insertedMiner;
  }

  // ...existing code for other methods...

}
import 'dotenv/config';

import {
  detectedMiners, 
  networkConnections, 
  scanSessions, 
  systemActivities,
  users,
  rfSignals,
  plcAnalysis,
  acousticSignatures,
  thermalSignatures,
  networkTraffic,
  type DetectedMiner, 
  type InsertMiner,
  type NetworkConnection,
  type InsertConnection,
  type ScanSession,
  type InsertScanSession,
  type SystemActivity,
  type InsertActivity,
  type InsertUser,
  type RfSignal,
  type InsertRfSignal,
  type PlcAnalysis,
  type InsertPlcAnalysis,
  type AcousticSignature,
  type InsertAcousticSignature,
  type ThermalSignature,
  type InsertThermalSignature,
  type NetworkTraffic,
  type InsertNetworkTraffic,
  type User
} from './schema';
import { eq, desc } from "drizzle-orm";
import 'dotenv/config';
import { db } from './db';

export interface IStorage {
  // User methods  
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Miner detection methods
  getDetectedMiners(): Promise<DetectedMiner[]>;
  getMinerById(id: number): Promise<DetectedMiner | undefined>;
  createMiner(miner: InsertMiner): Promise<DetectedMiner>;
  updateMiner(id: number, updates: Partial<InsertMiner>): Promise<DetectedMiner | undefined>;
  getActiveMiners(): Promise<DetectedMiner[]>;
  getMinersInArea(bounds: { north: number; south: number; east: number; west: number }): Promise<DetectedMiner[]>;

  // Network connections
  getNetworkConnections(): Promise<NetworkConnection[]>;
  createConnection(connection: InsertConnection): Promise<NetworkConnection>;
  getConnectionsByMiner(minerId: number): Promise<NetworkConnection[]>;

  // Scan sessions
  getScanSessions(): Promise<ScanSession[]>;
  createScanSession(session: InsertScanSession): Promise<ScanSession>;
  updateScanSession(id: number, updates: Partial<InsertScanSession>): Promise<ScanSession | undefined>;
  getActiveScanSessions(): Promise<ScanSession[]>;

  // System activities
  getRecentActivities(limit?: number): Promise<SystemActivity[]>;
  createActivity(activity: InsertActivity): Promise<SystemActivity>;

  // Scan Sessions
  getScanSessions(): Promise<ScanSession[]>;
  createScanSession(session: InsertScanSession): Promise<ScanSession>;
  updateScanSession(id: number, updates: Partial<InsertScanSession>): Promise<ScanSession | undefined>;
  getActiveScanSessions(): Promise<ScanSession[]>;

  // RF Signal Analysis
  getRfSignals(): Promise<RfSignal[]>;
  createRfSignal(signal: InsertRfSignal): Promise<RfSignal>;
  getRfSignalsByLocation(location: string): Promise<RfSignal[]>;

  // PLC Analysis
  getPlcAnalyses(): Promise<PlcAnalysis[]>;
  createPlcAnalysis(analysis: InsertPlcAnalysis): Promise<PlcAnalysis>;

  // Acoustic Signatures
  getAcousticSignatures(): Promise<AcousticSignature[]>;
  createAcousticSignature(signature: InsertAcousticSignature): Promise<AcousticSignature>;

  // Thermal Signatures
  getThermalSignatures(): Promise<ThermalSignature[]>;
  createThermalSignature(signature: InsertThermalSignature): Promise<ThermalSignature>;

  // Network Traffic
  getNetworkTraffic(): Promise<NetworkTraffic[]>;
  createNetworkTraffic(traffic: InsertNetworkTraffic): Promise<NetworkTraffic>;
  getStratumConnections(): Promise<NetworkTraffic[]>;

  // Session store for authentication
  sessionStore: any;

  // Statistics
  getStatistics(): Promise<{
    totalDevices: number;
    confirmedMiners: number;
    suspiciousDevices: number;
    totalPowerConsumption: number;
    networkHealth: number;
    rfSignalsDetected: number;
    acousticSignatures: number;
    thermalAnomalies: number;
  }>;
}

interface Statistics {
    totalDevices: number;
    confirmedMiners: number;
    suspiciousDevices: number;
    totalPowerConsumption: number;
    networkHealth: number;
    rfSignalsDetected: number;
    acousticSignatures: number;
    thermalAnomalies: number;
  }

// استفاده از db برای ذخیره‌سازی داده‌ها


db.exec(`
CREATE TABLE IF NOT EXISTS miners (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ip TEXT,
  mac TEXT,
  device_type TEXT,
  open_ports TEXT,
  suspicion_score INTEGER,
  city TEXT,
  country TEXT,
  latitude REAL,
  longitude REAL,
  hostname TEXT,
  status TEXT,
  detection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
  power_consumption REAL,
  hash_rate TEXT,
  response_time INTEGER,
  is_active BOOLEAN DEFAULT 1,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS activities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT,
  description TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
`);

export function getStatistics() {
  const stats = {
    totalDevices: 0,
    confirmedMiners: 0,
    suspiciousDevices: 0,
    totalPowerConsumption: 0
  };

  try {
    const miners = db.select().from(detectedMiners).all();
    stats.totalDevices = miners.length;
    stats.confirmedMiners = miners.filter(m => m.confidenceScore >= 80).length;
    stats.suspiciousDevices = miners.filter(m => m.confidenceScore >= 50 && m.confidenceScore < 80).length;
    stats.totalPowerConsumption = miners.reduce((sum, m) => sum + (m.powerConsumption || 0), 0);
  } catch (error) {
    console.error('Error getting statistics:', error);
  }

  return Promise.resolve(stats);
}

export function getMiners() {
  return db.prepare('SELECT * FROM miners ORDER BY suspicion_score DESC').all();
}

export function getActivities() {
  return db.prepare('SELECT * FROM activities ORDER BY timestamp DESC LIMIT 100').all();
}

function isValidIP(ip: string): boolean {
  // IPv4 validation
  return /^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip);
}
function isValidPort(port: number): boolean {
  return Number.isInteger(port) && port > 0 && port < 65536;
}
function isValidOpenPorts(open_ports: string): boolean {
  // open_ports: comma-separated string of ports
  return open_ports.split(',').every(p => isValidPort(Number(p.trim())));
}

export function addMiner(miner: any) {
  if (!isValidIP(miner.ip)) {
    console.error('Invalid IP address:', miner.ip);
    return;
  }
  if (miner.open_ports && !isValidOpenPorts(miner.open_ports)) {
    console.error('Invalid open_ports:', miner.open_ports);
    return;
  }
  const stmt = db.prepare(`INSERT INTO miners (ip, mac, device_type, open_ports, suspicion_score, city, country, latitude, longitude, hostname, status, power_consumption, hash_rate, response_time, is_active, notes) VALUES (@ip, @mac, @device_type, @open_ports, @suspicion_score, @city, @country, @latitude, @longitude, @hostname, @status, @power_consumption, @hash_rate, @response_time, @is_active, @notes)`);
  stmt.run(miner);
}

export function addActivity(activity: any) {
  const stmt = db.prepare(`INSERT INTO activities (type, description) VALUES (?, ?)`);
  stmt.run(activity.type, activity.description);
}


export class MemStorage implements IStorage {
    sessionStore: any;
    async getUser(id: number): Promise<User | undefined> {
        return undefined;
    }
    async getUserByUsername(username: string): Promise<User | undefined> {
        return undefined;
    }
    async createUser(user: InsertUser): Promise<User> {
        return user as User;
    }
    async getDetectedMiners(): Promise<DetectedMiner[]> {
        return [];
    }
    async getMinerById(id: number): Promise<DetectedMiner | undefined> {
        return undefined;
    }
    async createMiner(miner: InsertMiner): Promise<DetectedMiner> {
        return miner as DetectedMiner;
    }
    async updateMiner(id: number, updates: Partial<InsertMiner>): Promise<DetectedMiner | undefined> {
        return undefined;
    }
    async getActiveMiners(): Promise<DetectedMiner[]> {
        return [];
    }
    async getMinersInArea(bounds: { north: number; south: number; east: number; west: number }): Promise<DetectedMiner[]> {
        return [];
    }
    async getNetworkConnections(): Promise<NetworkConnection[]> {
        return [];
    }
    async createConnection(connection: InsertConnection): Promise<NetworkConnection> {
        return connection as NetworkConnection;
    }
    async getConnectionsByMiner(minerId: number): Promise<NetworkConnection[]> {
        return [];
    }
    async getScanSessions(): Promise<ScanSession[]> {
        return [];
    }
    async createScanSession(session: InsertScanSession): Promise<ScanSession> {
        return session as ScanSession;
    }
    async updateScanSession(id: number, updates: Partial<InsertScanSession>): Promise<ScanSession | undefined> {
        return undefined;
    }
    async getActiveScanSessions(): Promise<ScanSession[]> {
        return [];
    }
    async getRecentActivities(limit?: number): Promise<SystemActivity[]> {
        return [];
    }
    async createActivity(activity: InsertActivity): Promise<SystemActivity> {
        return activity as SystemActivity;
    }
    async getRfSignals(): Promise<RfSignal[]> {
        return [];
    }
    async createRfSignal(signal: InsertRfSignal): Promise<RfSignal> {
        return signal as RfSignal;
    }
    async getRfSignalsByLocation(location: string): Promise<RfSignal[]> {
        return [];
    }
    async getPlcAnalyses(): Promise<PlcAnalysis[]> {
        return [];
    }
    async createPlcAnalysis(analysis: InsertPlcAnalysis): Promise<PlcAnalysis> {
        return analysis as PlcAnalysis;
    }
    async getAcousticSignatures(): Promise<AcousticSignature[]> {
        return [];
    }
    async createAcousticSignature(signature: InsertAcousticSignature): Promise<AcousticSignature> {
        return signature as AcousticSignature;
    }
    async getThermalSignatures(): Promise<ThermalSignature[]> {
        return [];
    }
    async createThermalSignature(signature: InsertThermalSignature): Promise<ThermalSignature> {
        return signature as ThermalSignature;
    }
    async getNetworkTraffic(): Promise<NetworkTraffic[]> {
        return [];
    }
    async createNetworkTraffic(traffic: InsertNetworkTraffic): Promise<NetworkTraffic> {
        return traffic as NetworkTraffic;
    }
    async getStratumConnections(): Promise<NetworkTraffic[]> {
        return [];
    }
    async getStatistics(): Promise<{
        totalDevices: number;
        confirmedMiners: number;
        suspiciousDevices: number;
        totalPowerConsumption: number;
        networkHealth: number;
        rfSignalsDetected: number;
        acousticSignatures: number;
        thermalAnomalies: number;
    }> {
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

export const storage = new DatabaseStorage();