#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Management System for National Miner Detection
سیستم مدیریت پایگاه داده برای سیستم جامع ملی کشف ماینرها
"""

import asyncio
import sqlite3
import logging
import json
from typing import List, Dict, Any, Optional, Tuple
import aiosqlite
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    mac_address = Column(String)
    hostname = Column(String)
    device_type = Column(String)
    last_seen = Column(DateTime)
    is_active = Column(Boolean, default=True)

class ScanResult(Base):
    __tablename__ = 'scan_results'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    scan_time = Column(DateTime)
    ports = Column(String)
    services = Column(String)
    os_info = Column(String)
    status = Column(String)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SQLAlchemy session factory
_engine = create_engine('sqlite:///ilam_mining.db')
Base.metadata.create_all(_engine)
_SessionFactory = sessionmaker(bind=_engine)

def get_session() -> Session:
    """Get a new database session"""
    return _SessionFactory()

class DatabaseManager:
    """سیستم مدیریت پایگاه داده برای ذخیره و بازیابی داده‌های تشخیص ماینر"""
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Detected Miners Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detected_miners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT,
                    hostname TEXT,
                    latitude REAL,
                    longitude REAL,
                    city TEXT,
                    detection_method TEXT,
                    power_consumption REAL,
                    hash_rate TEXT,
                    device_type TEXT,
                    process_name TEXT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    network_usage REAL,
                    gpu_usage REAL,
                    detection_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    suspicion_score INTEGER,
                    confidence_score INTEGER,
                    threat_level TEXT,
                    notes TEXT,
                    is_active TEXT DEFAULT 'true',
                    scan_session_id TEXT
                )
            """)
            
            # Network Connections Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    local_address TEXT NOT NULL,
                    local_port INTEGER NOT NULL,
                    remote_address TEXT,
                    remote_port INTEGER,
                    protocol TEXT NOT NULL,
                    status TEXT NOT NULL,
                    process_name TEXT,
                    detection_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    miner_id INTEGER,
                    FOREIGN KEY (miner_id) REFERENCES detected_miners(id)
                )
            """)
            
            # Scan Sessions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_sessions (
                    id TEXT PRIMARY KEY,
                    session_type TEXT NOT NULL,
                    ip_range TEXT,
                    ports TEXT,
                    start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    devices_found INTEGER DEFAULT 0,
                    miners_detected INTEGER DEFAULT 0,
                    errors TEXT,
                    priority TEXT DEFAULT 'normal'
                )
            """)
            
            # System Activities Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # RF Signals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rf_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frequency REAL NOT NULL,
                    signal_strength REAL NOT NULL,
                    bandwidth REAL,
                    modulation_type TEXT,
                    noise_floor REAL,
                    snr REAL,
                    location TEXT,
                    device_signature TEXT,
                    switching_pattern TEXT,
                    harmonics TEXT,
                    detection_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    confidence_level REAL NOT NULL
                )
            """)
            
            # Power Line Communication Analysis Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plc_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    power_line_freq REAL NOT NULL,
                    harmonic_distortion REAL,
                    power_quality REAL,
                    voltage_fluctuation REAL,
                    current_spikes TEXT,
                    power_factor REAL,
                    location TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    miner_indicators TEXT
                )
            """)
            
            # Acoustic Signatures Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS acoustic_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fan_speed_rpm INTEGER,
                    acoustic_fingerprint TEXT,
                    frequency_spectrum TEXT,
                    noise_level REAL,
                    fan_noise_pattern TEXT,
                    cooling_system_type TEXT,
                    device_model TEXT,
                    location TEXT,
                    recording_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    match_confidence REAL
                )
            """)
            
            # Thermal Signatures Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thermal_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    surface_temp REAL,
                    ambient_temp REAL,
                    temp_difference REAL,
                    heat_pattern TEXT,
                    thermal_image TEXT,
                    hotspot_count INTEGER,
                    thermal_efficiency REAL,
                    location TEXT,
                    capture_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    device_type TEXT
                )
            """)
            
            # Network Traffic Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_traffic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    src_ip TEXT NOT NULL,
                    dst_ip TEXT NOT NULL,
                    src_port INTEGER,
                    dst_port INTEGER,
                    protocol TEXT NOT NULL,
                    packet_size INTEGER,
                    payload_hash TEXT,
                    stratum_protocol TEXT DEFAULT 'false',
                    pool_address TEXT,
                    miner_agent TEXT,
                    session_duration INTEGER,
                    data_volume INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    threat_level TEXT DEFAULT 'low'
                )
            """)
            
            # Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'admin',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def get_connection(self) -> aiosqlite.Connection:
        """Get async database connection"""
        return await aiosqlite.connect(self.db_path)
    
    async def close_connection(self, conn: aiosqlite.Connection):
        """Close async database connection"""
        await conn.close()
    
    async def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a query"""
        conn = await self.get_connection()
        try:
            await conn.execute(query, params)
            await conn.commit()
        finally:
            await self.close_connection(conn)
    
    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Fetch one row from database"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        finally:
            await self.close_connection(conn)
    
    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Fetch all rows from database"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            await self.close_connection(conn)
    
    async def fetch_val(self, query: str, params: Tuple = ()) -> Any:
        """Fetch single value from database"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return row[0] if row else None
        finally:
            await self.close_connection(conn)
    
    async def get_detected_miners(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get list of detected miners"""
        return await self.fetch_all(
            "SELECT * FROM detected_miners ORDER BY detection_time DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
    
    async def get_miner_by_id(self, miner_id: int) -> Optional[Dict]:
        """Get miner by ID"""
        return await self.fetch_one("SELECT * FROM detected_miners WHERE id = ?", (miner_id,))
    
    async def create_miner(self, miner_data: Dict) -> int:
        """Create new miner record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO detected_miners (
                    ip_address, mac_address, hostname, latitude, longitude, city,
                    detection_method, power_consumption, hash_rate, device_type,
                    process_name, cpu_usage, memory_usage, network_usage, gpu_usage,
                    suspicion_score, confidence_score, threat_level, notes, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                miner_data.get('ip_address', ''),
                miner_data.get('mac_address'),
                miner_data.get('hostname'),
                miner_data.get('latitude'),
                miner_data.get('longitude'),
                miner_data.get('city'),
                miner_data.get('detection_method', ''),
                miner_data.get('power_consumption'),
                miner_data.get('hash_rate'),
                miner_data.get('device_type', 'unknown'),
                miner_data.get('process_name'),
                miner_data.get('cpu_usage'),
                miner_data.get('memory_usage'),
                miner_data.get('network_usage'),
                miner_data.get('gpu_usage'),
                miner_data.get('suspicion_score', 0),
                miner_data.get('confidence_score', 0),
                miner_data.get('threat_level', 'medium'),
                miner_data.get('notes'),
                miner_data.get('is_active', 'true')
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def update_miner(self, miner_id: int, updates: Dict) -> bool:
        """Update miner record"""
        conn = await self.get_connection()
        try:
            # Build update query dynamically
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(miner_id)
            
            query = f"UPDATE detected_miners SET {set_clause} WHERE id = ?"
            await conn.execute(query, values)
            await conn.commit()
            return True
        finally:
            await self.close_connection(conn)
    
    async def get_miners_in_area(self, bounds: Dict) -> List[Dict]:
        """Get miners within geographical bounds"""
        return await self.fetch_all("""
            SELECT * FROM detected_miners 
            WHERE latitude BETWEEN ? AND ? 
            AND longitude BETWEEN ? AND ?
        """, (
            bounds['south'],
            bounds['north'],
            bounds['west'],
            bounds['east']
        ))
    
    async def get_active_miners(self) -> List[Dict]:
        """Get active miners"""
        return await self.fetch_all("SELECT * FROM detected_miners WHERE is_active = 'true'")
    
    async def get_network_connections(self, miner_id: Optional[int] = None) -> List[Dict]:
        """Get network connections"""
        if miner_id:
            return await self.fetch_all(
                "SELECT * FROM network_connections WHERE miner_id = ?",
                (miner_id,)
            )
        return await self.fetch_all("SELECT * FROM network_connections")
    
    async def create_connection(self, connection_data: Dict) -> int:
        """Create new network connection record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO network_connections (
                    local_address, local_port, remote_address, remote_port,
                    protocol, status, process_name, miner_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                connection_data.get('local_address', ''),
                connection_data.get('local_port', 0),
                connection_data.get('remote_address'),
                connection_data.get('remote_port'),
                connection_data.get('protocol', ''),
                connection_data.get('status', ''),
                connection_data.get('process_name'),
                connection_data.get('miner_id')
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_scan_sessions(self, limit: int = 50) -> List[Dict]:
        """Get scan sessions"""
        return await self.fetch_all(
            "SELECT * FROM scan_sessions ORDER BY start_time DESC LIMIT ?",
            (limit,)
        )
    
    async def create_scan_session(self, session_data: Dict) -> str:
        """Create new scan session"""
        conn = await self.get_connection()
        try:
            session_id = session_data.get('id')
            await conn.execute("""
                INSERT INTO scan_sessions (
                    id, session_type, ip_range, ports, status, priority
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                session_data.get('session_type', ''),
                session_data.get('ip_range'),
                json.dumps(session_data.get('ports', [])),
                session_data.get('status', 'running'),
                session_data.get('priority', 'normal')
            ))
            await conn.commit()
            return session_id
        finally:
            await self.close_connection(conn)
    
    async def update_scan_session(self, session_id: str, updates: Dict) -> bool:
        """Update scan session"""
        conn = await self.get_connection()
        try:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(session_id)
            
            query = f"UPDATE scan_sessions SET {set_clause} WHERE id = ?"
            await conn.execute(query, values)
            await conn.commit()
            return True
        finally:
            await self.close_connection(conn)
    
    async def get_active_scan_sessions(self) -> List[Dict]:
        """Get active scan sessions"""
        return await self.fetch_all("SELECT * FROM scan_sessions WHERE status = 'running'")
    
    async def get_recent_activities(self, limit: int = 100) -> List[Dict]:
        """Get recent system activities"""
        return await self.fetch_all(
            "SELECT * FROM system_activities ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
    
    async def create_activity(self, activity_data: Dict) -> int:
        """Create new system activity"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO system_activities (
                    activity_type, description, severity, metadata
                ) VALUES (?, ?, ?, ?)
            """, (
                activity_data.get('activity_type', ''),
                activity_data.get('description', ''),
                activity_data.get('severity', 'info'),
                json.dumps(activity_data.get('metadata', {}))
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_rf_signals(self, limit: int = 100) -> List[Dict]:
        """Get RF signals"""
        return await self.fetch_all(
            "SELECT * FROM rf_signals ORDER BY detection_time DESC LIMIT ?",
            (limit,)
        )
    
    async def create_rf_signal(self, signal_data: Dict) -> int:
        """Create new RF signal record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO rf_signals (
                    frequency, signal_strength, bandwidth, modulation_type,
                    noise_floor, snr, location, device_signature,
                    switching_pattern, harmonics, confidence_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_data.get('frequency', 0.0),
                signal_data.get('signal_strength', 0.0),
                signal_data.get('bandwidth'),
                signal_data.get('modulation_type'),
                signal_data.get('noise_floor'),
                signal_data.get('snr'),
                signal_data.get('location'),
                signal_data.get('device_signature'),
                signal_data.get('switching_pattern'),
                json.dumps(signal_data.get('harmonics', [])),
                signal_data.get('confidence_level', 0.0)
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_rf_signals_by_location(self, location: str) -> List[Dict]:
        """Get RF signals by location"""
        return await self.fetch_all(
            "SELECT * FROM rf_signals WHERE location = ? ORDER BY detection_time DESC",
            (location,)
        )
    
    async def get_plc_analyses(self, limit: int = 100) -> List[Dict]:
        """Get PLC analyses"""
        return await self.fetch_all(
            "SELECT * FROM plc_analysis ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
    
    async def create_plc_analysis(self, analysis_data: Dict) -> int:
        """Create new PLC analysis record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO plc_analysis (
                    power_line_freq, harmonic_distortion, power_quality,
                    voltage_fluctuation, current_spikes, power_factor,
                    location, miner_indicators
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data.get('power_line_freq', 0.0),
                analysis_data.get('harmonic_distortion'),
                analysis_data.get('power_quality'),
                analysis_data.get('voltage_fluctuation'),
                json.dumps(analysis_data.get('current_spikes', [])),
                analysis_data.get('power_factor'),
                analysis_data.get('location'),
                json.dumps(analysis_data.get('miner_indicators', {}))
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_acoustic_signatures(self, limit: int = 100) -> List[Dict]:
        """Get acoustic signatures"""
        return await self.fetch_all(
            "SELECT * FROM acoustic_signatures ORDER BY recording_time DESC LIMIT ?",
            (limit,)
        )
    
    async def create_acoustic_signature(self, signature_data: Dict) -> int:
        """Create new acoustic signature record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO acoustic_signatures (
                    fan_speed_rpm, acoustic_fingerprint, frequency_spectrum,
                    noise_level, fan_noise_pattern, cooling_system_type,
                    device_model, location, match_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signature_data.get('fan_speed_rpm'),
                signature_data.get('acoustic_fingerprint'),
                json.dumps(signature_data.get('frequency_spectrum', {})),
                signature_data.get('noise_level'),
                signature_data.get('fan_noise_pattern'),
                signature_data.get('cooling_system_type'),
                signature_data.get('device_model'),
                signature_data.get('location'),
                signature_data.get('match_confidence', 0.0)
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_thermal_signatures(self, limit: int = 100) -> List[Dict]:
        """Get thermal signatures"""
        return await self.fetch_all(
            "SELECT * FROM thermal_signatures ORDER BY capture_time DESC LIMIT ?",
            (limit,)
        )
    
    async def create_thermal_signature(self, signature_data: Dict) -> int:
        """Create new thermal signature record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO thermal_signatures (
                    surface_temp, ambient_temp, temp_difference, heat_pattern,
                    thermal_image, hotspot_count, thermal_efficiency, location,
                    device_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                signature_data.get('surface_temp'),
                signature_data.get('ambient_temp'),
                signature_data.get('temp_difference'),
                signature_data.get('heat_pattern'),
                signature_data.get('thermal_image'),
                signature_data.get('hotspot_count'),
                signature_data.get('thermal_efficiency'),
                signature_data.get('location'),
                signature_data.get('device_type')
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_network_traffic(self, limit: int = 100) -> List[Dict]:
        """Get network traffic records"""
        return await self.fetch_all(
            "SELECT * FROM network_traffic ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
    
    async def create_network_traffic(self, traffic_data: Dict) -> int:
        """Create new network traffic record"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO network_traffic (
                    src_ip, dst_ip, src_port, dst_port, protocol, packet_size,
                    payload_hash, stratum_protocol, pool_address, miner_agent,
                    session_duration, data_volume, threat_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                traffic_data.get('src_ip', ''),
                traffic_data.get('dst_ip', ''),
                traffic_data.get('src_port'),
                traffic_data.get('dst_port'),
                traffic_data.get('protocol', ''),
                traffic_data.get('packet_size'),
                traffic_data.get('payload_hash'),
                traffic_data.get('stratum_protocol', 'false'),
                traffic_data.get('pool_address'),
                traffic_data.get('miner_agent'),
                traffic_data.get('session_duration'),
                traffic_data.get('data_volume'),
                traffic_data.get('threat_level', 'low')
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def get_stratum_connections(self) -> List[Dict]:
        """Get network traffic with Stratum protocol"""
        return await self.fetch_all("SELECT * FROM network_traffic WHERE stratum_protocol = 'true'")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return await self.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
    
    async def create_user(self, user_data: Dict) -> int:
        """Create new user"""
        conn = await self.get_connection()
        try:
            cursor = await conn.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (
                user_data.get('username', ''),
                user_data.get('password', ''),
                user_data.get('role', 'user')
            ))
            await conn.commit()
            return cursor.lastrowid
        finally:
            await self.close_connection(conn)
    
    async def update_user_last_login(self, user_id: int, timestamp: str) -> bool:
        """Update user's last login timestamp"""
        return await self.update_user(user_id, {'last_login': timestamp})
    
    async def update_user(self, user_id: int, updates: Dict) -> bool:
        """Update user record"""
        conn = await self.get_connection()
        try:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(user_id)
            
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            await conn.execute(query, values)
            await conn.commit()
            return True
        finally:
            await self.close_connection(conn)
    
    async def get_statistics(self) -> Dict:
        """Get system statistics"""
        try:
            total_miners = await self.fetch_val("SELECT COUNT(*) FROM detected_miners")
            active_miners = await self.fetch_val("SELECT COUNT(*) FROM detected_miners WHERE is_active = 'true'")
            confirmed_miners = await self.fetch_val("SELECT COUNT(*) FROM detected_miners WHERE confidence_score >= 80")
            suspicious_devices = await self.fetch_val("SELECT COUNT(*) FROM detected_miners WHERE confidence_score >= 50 AND confidence_score < 80")
            total_power = await self.fetch_val("SELECT SUM(power_consumption) FROM detected_miners WHERE power_consumption IS NOT NULL") or 0
            rf_signals = await self.fetch_val("SELECT COUNT(*) FROM rf_signals")
            acoustic_sigs = await self.fetch_val("SELECT COUNT(*) FROM acoustic_signatures")
            thermal_anomalies = await self.fetch_val("SELECT COUNT(*) FROM thermal_signatures")
            network_health = 100  # Placeholder
            
            return {
                "totalDevices": total_miners,
                "confirmedMiners": confirmed_miners,
                "suspiciousDevices": suspicious_devices,
                "totalPowerConsumption": total_power,
                "networkHealth": network_health,
                "rfSignalsDetected": rf_signals,
                "acousticSignatures": acoustic_sigs,
                "thermalAnomalies": thermal_anomalies
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "totalDevices": 0,
                "confirmedMiners": 0,
                "suspiciousDevices": 0,
                "totalPowerConsumption": 0,
                "networkHealth": 0,
                "rfSignalsDetected": 0,
                "acousticSignatures": 0,
                "thermalAnomalies": 0
            }

# Global instance
database = DatabaseManager()

def get_database() -> DatabaseManager:
    """Get database instance"""
    return database
