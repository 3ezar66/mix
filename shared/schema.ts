import { sqliteTable, text, integer, real, type SQLiteTable } from 'drizzle-orm/sqlite-core';
import { type InferSelectModel } from 'drizzle-orm';
import { IsDrizzleTable } from 'drizzle-orm/table';
import { createInsertSchema } from 'drizzle-zod';
import { z } from 'zod';

// Miner table and schema
export const miners = sqliteTable('miners', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  location: text('location').notNull(),
  status: text('status', { enum: ['active', 'inactive'] }).notNull(),
  detectedAt: integer('detected_at', { mode: 'timestamp' }).notNull(),
  confidence: real('confidence').notNull()
});

export const insertMinerSchema = createInsertSchema(miners);

// Types
export type Miner = InferSelectModel<typeof miners>;
export type InsertMiner = z.infer<typeof insertMinerSchema>;

// Connection schema
export const createConnectionSchema = z.object({
  deviceId: z.string(),
  timestamp: z.number()
});

// Scan session schema
export const insertScanSessionSchema = z.object({
  startTime: z.number(),
  endTime: z.number(),
  status: z.enum(['completed', 'failed', 'in_progress'])
});

// Activity schema
export const insertActivitySchema = z.object({
  type: z.enum(['scan', 'detection', 'alert']),
  details: z.string(),
  timestamp: z.number()
});

// User table and schema
export const users = sqliteTable('users', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  username: text('username').notNull(),
  password: text('password').notNull(),
  role: text('role', { enum: ['admin', 'user'] }).notNull()
});

export const insertUserSchema = createInsertSchema(users);

// RF Signals table and schema
export const rfSignals = sqliteTable('rf_signals', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  frequency: real('frequency').notNull(),
  signalStrength: real('signal_strength').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }).notNull()
});

export const insertRfSignalSchema = createInsertSchema(rfSignals);

// PLC Analysis table and schema
export const plcAnalysis = sqliteTable('plc_analysis', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  powerLineFreq: real('power_line_freq').notNull(),
  harmonics: text('harmonics').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }).notNull()
});

export const insertPlcAnalysisSchema = createInsertSchema(plcAnalysis);

// Acoustic Signatures table and schema
export const acousticSignatures = sqliteTable('acoustic_signatures', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  frequency: real('frequency').notNull(),
  amplitude: real('amplitude').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }).notNull()
});

export const insertAcousticSignatureSchema = createInsertSchema(acousticSignatures);

// Thermal Signatures table and schema
export const thermalSignatures = sqliteTable('thermal_signatures', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  temperature: real('temperature').notNull(),
  location: text('location').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }).notNull()
});

export const insertThermalSignatureSchema = createInsertSchema(thermalSignatures);

// Scan Sessions table and schema
export const scanSessions = sqliteTable('scan_sessions', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  startTime: integer('start_time', { mode: 'timestamp' }).notNull(),
  endTime: integer('end_time', { mode: 'timestamp' }).notNull(),
  status: text('status', { enum: ['completed', 'failed', 'in_progress'] }).notNull()
});

export const insertScanSessionSchema = createInsertSchema(scanSessions);

// Types
export type ScanSession = InferSelectModel<typeof scanSessions>;
export type InsertScanSession = z.infer<typeof insertScanSessionSchema>;

// Network Traffic table and schema
export const networkTraffic = sqliteTable('network_traffic', {
  [IsDrizzleTable]: true,
  id: integer('id').primaryKey(),
  srcIp: text('src_ip').notNull(),
  dstIp: text('dst_ip').notNull(),
  protocol: text('protocol').notNull(),
  timestamp: integer('timestamp', { mode: 'timestamp' }).notNull()
});

export const insertNetworkTrafficSchema = createInsertSchema(networkTraffic);

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export type RfSignal = typeof rfSignals.$inferSelect;
export type InsertRfSignal = typeof rfSignals.$inferInsert;

export type PlcAnalysis = typeof plcAnalysis.$inferSelect;
export type InsertPlcAnalysis = typeof plcAnalysis.$inferInsert;

export type AcousticSignature = typeof acousticSignatures.$inferSelect;
export type InsertAcousticSignature = typeof acousticSignatures.$inferInsert;

export type ThermalSignature = typeof thermalSignatures.$inferSelect;
export type InsertThermalSignature = typeof thermalSignatures.$inferInsert;

export type NetworkTraffic = typeof networkTraffic.$inferSelect;
export type InsertNetworkTraffic = typeof networkTraffic.$inferInsert;

export type Miner = typeof miners.$inferSelect;
export type InsertMiner = typeof miners.$inferInsert;

