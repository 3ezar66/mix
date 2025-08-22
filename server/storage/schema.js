import { pgTable, text, timestamp, boolean, integer, jsonb } from 'drizzle-orm/pg-core';
export const devices = pgTable('devices', {
    id: text('id').primaryKey(),
    ip: text('ip').notNull().unique(),
    mac: text('mac').notNull(),
    hostname: text('hostname').notNull(),
    first_seen: timestamp('first_seen').notNull(),
    last_seen: timestamp('last_seen').notNull(),
    status: text('status').notNull(),
});
export const scanResults = pgTable('scan_results', {
    id: text('id').primaryKey(),
    device_id: text('device_id')
        .notNull()
        .references(() => devices.id),
    timestamp: timestamp('timestamp').notNull(),
    is_mining: boolean('is_mining').notNull(),
    confidence: integer('confidence').notNull(),
    ports: integer('ports').array(),
    mining_pools: text('mining_pools').array(),
    resource_usage: jsonb('resource_usage').notNull(),
});
export const alerts = pgTable('alerts', {
    id: text('id').primaryKey(),
    device_id: text('device_id')
        .notNull()
        .references(() => devices.id),
    timestamp: timestamp('timestamp').notNull(),
    type: text('type').notNull(),
    severity: text('severity').notNull(),
    message: text('message').notNull(),
    resolved: boolean('resolved').notNull().default(false),
});
