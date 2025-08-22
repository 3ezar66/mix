const bcrypt = require('bcrypt');
const sqlite3 = require('sqlite3');
const db = new sqlite3.Database('ilam_mining.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS detected_miners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    mac_address TEXT,
    hostname TEXT,
    latitude REAL,
    longitude REAL,
    city TEXT,
    detection_method TEXT NOT NULL,
    suspicion_score INTEGER DEFAULT 0,
    confidence_score INTEGER DEFAULT 0,
    threat_level TEXT DEFAULT 'low',
    power_consumption REAL,
    hash_rate TEXT,
    device_type TEXT,
    process_name TEXT,
    notes TEXT,
    is_active TEXT DEFAULT 'true',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS system_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    description TEXT,
    user_id INTEGER,
    ip_address TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);

  const hashedPassword = bcrypt.hashSync('admin123', 10);
  db.run(`INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', ?, 'admin')`, [hashedPassword], (err) => {
    if (err) {
      console.error('❌ خطا در افزودن کاربر پیش‌فرض:', err.message);
    } else {
      console.log('✅ دیتابیس و کاربر پیش‌فرض با موفقیت ایجاد شدند');
    }
    db.close();
  });
});
