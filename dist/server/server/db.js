import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import * as schema from '../shared/schema';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
const __dirname = dirname(fileURLToPath(import.meta.url));
const dbPath = join(__dirname, '../ilam_mining.db');
// Create database file if it doesn't exist
if (!fs.existsSync(dbPath)) {
    fs.writeFileSync(dbPath, '');
}
const sqlite = new Database(dbPath);
export const db = drizzle(sqlite, { schema });
// Initialize the schema using drizzle-orm migrations
async function initializeDatabase() {
    try {
        await migrate(db, {
            migrationsFolder: join(__dirname, '../drizzle')
        });
        console.log('Database schema initialized successfully');
    }
    catch (error) {
        console.error('Error initializing database:', error);
        process.exit(1);
    }
    // Initialize with default settings
    const defaultSettings = {
        minConfidenceScore: 70,
        powerThreshold: 1500,
        rfDetectionEnabled: true,
        aiAnalysisEnabled: true
    };
    // Only insert settings if they don't exist
    const existingActivities = db.select().from(schema.systemActivities).all();
    const settingsExist = existingActivities.some(a => a.activityType === 'setting');
    if (!settingsExist) {
        for (const [key, value] of Object.entries(defaultSettings)) {
            db.insert(schema.systemActivities)
                .values({
                activityType: 'setting',
                description: key,
                severity: 'info',
                metadata: JSON.stringify({ value }),
                timestamp: new Date().toISOString()
            })
                .run();
        }
    }
}
initializeDatabase().catch(console.error);
