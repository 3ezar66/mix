import { drizzle } from 'drizzle-orm/better-sqlite3';
import { migrate } from 'drizzle-orm/better-sqlite3/migrator';
import * as schema from '../shared/schema';
import { join } from 'path';
import fs from 'fs';
import Database from 'better-sqlite3';

const __dirname = process.cwd();
const dbPath = join(__dirname, '../ilam_mining.db');

// Create database file if it doesn't exist
if (!fs.existsSync(dbPath)) {
  fs.writeFileSync(dbPath, '');
}

const betterSqlite = new Database(dbPath);
export const db = drizzle(betterSqlite, { schema });

// Initialize the schema using drizzle-orm migrations
async function initializeDatabase() {
  try {
    await migrate(db, {
      migrationsFolder: join(__dirname, '../drizzle')
    });
    console.log('Database schema initialized successfully');
  } catch (error) {
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
  const existingSettings = db.select().from(schema.networkTraffic).all();
  
  // Add [IsDrizzleTable] symbol to tables
  [schema.networkTraffic, schema.miners].forEach(table => {
    Object.defineProperty(table, Symbol.for('IsDrizzleTable'), {
      value: true,
      enumerable: false,
      configurable: false
    });
  });
  
  if (existingSettings.length === 0) {
    db.insert(schema.networkTraffic)
      .values({
        protocol: 'system',
        source: 'initialization',
        destination: 'system',
        timestamp: new Date().toISOString(),
        bytesTransferred: 0,
        duration: 0
      })
      .run();
  }
}

export default initializeDatabase;