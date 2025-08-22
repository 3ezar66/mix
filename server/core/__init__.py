#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Logic and Shared Utilities for the Detection System
منطق اصلی و ابزارهای مشترک برای سیستم تشخیص
"""

import asyncio
import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiosqlite
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DetectionStatus(Enum):
    """وضعیت‌های تشخیص"""
    PENDING = "pending"
    SCANNING = "scanning"
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"

class MinerType(Enum):
    """انواع ماینر"""
    ASIC = "asic"
    GPU = "gpu"
    CPU = "cpu"
    UNKNOWN = "unknown"

class ScanType(Enum):
    """انواع اسکن"""
    NETWORK = "network"
    RF = "rf"
    ACOUSTIC = "acoustic"
    THERMAL = "thermal"
    POWER = "power"
    COMPREHENSIVE = "comprehensive"

@dataclass
class DetectionResult:
    """نتیجه تشخیص"""
    id: str
    timestamp: datetime
    ip_address: str
    mac_address: Optional[str]
    location: Dict[str, float]  # lat, lng
    confidence: float
    miner_type: MinerType
    scan_type: ScanType
    status: DetectionStatus
    details: Dict[str, Any]
    owner_info: Optional[Dict[str, Any]] = None

@dataclass
class ScanSession:
    """جلسه اسکن"""
    id: str
    start_time: datetime
    end_time: Optional[datetime]
    scan_type: ScanType
    target_range: str
    results: List[DetectionResult]
    status: str

class CoreSystem:
    """
    سیستم اصلی برای مدیریت منطق کسب و کار
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.active_sessions: Dict[str, ScanSession] = {}
        self.detection_history: List[DetectionResult] = []
        
    async def initialize_database(self):
        """راه‌اندازی پایگاه داده"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS detection_results (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        ip_address TEXT,
                        mac_address TEXT,
                        latitude REAL,
                        longitude REAL,
                        confidence REAL,
                        miner_type TEXT,
                        scan_type TEXT,
                        status TEXT,
                        details TEXT,
                        owner_info TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS scan_sessions (
                        id TEXT PRIMARY KEY,
                        start_time TEXT,
                        end_time TEXT,
                        scan_type TEXT,
                        target_range TEXT,
                        status TEXT
                    )
                """)
                
                await db.commit()
                logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    async def create_scan_session(self, scan_type: ScanType, target_range: str) -> str:
        """ایجاد جلسه اسکن جدید"""
        session_id = hashlib.md5(f"{datetime.now().isoformat()}{target_range}".encode()).hexdigest()
        
        session = ScanSession(
            id=session_id,
            start_time=datetime.now(),
            end_time=None,
            scan_type=scan_type,
            target_range=target_range,
            results=[],
            status="active"
        )
        
        self.active_sessions[session_id] = session
        
        # Save to database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO scan_sessions (id, start_time, scan_type, target_range, status)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, session.start_time.isoformat(), scan_type.value, target_range, "active"))
            await db.commit()
        
        logger.info(f"🔍 New scan session created: {session_id}")
        return session_id
    
    async def add_detection_result(self, session_id: str, result: DetectionResult):
        """افزودن نتیجه تشخیص به جلسه"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].results.append(result)
            self.detection_history.append(result)
            
            # Save to database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO detection_results 
                    (id, timestamp, ip_address, mac_address, latitude, longitude, 
                     confidence, miner_type, scan_type, status, details, owner_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.id,
                    result.timestamp.isoformat(),
                    result.ip_address,
                    result.mac_address,
                    result.location.get('lat', 0),
                    result.location.get('lng', 0),
                    result.confidence,
                    result.miner_type.value,
                    result.scan_type.value,
                    result.status.value,
                    json.dumps(result.details),
                    json.dumps(result.owner_info) if result.owner_info else None
                ))
                await db.commit()
            
            logger.info(f"🎯 Detection result added: {result.ip_address}")
    
    async def get_session_results(self, session_id: str) -> List[DetectionResult]:
        """دریافت نتایج جلسه اسکن"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].results
        return []
    
    async def get_all_detections(self) -> List[DetectionResult]:
        """دریافت تمام تشخیص‌ها"""
        return self.detection_history
    
    async def end_scan_session(self, session_id: str):
        """پایان دادن به جلسه اسکن"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.end_time = datetime.now()
            session.status = "completed"
            
            # Update database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE scan_sessions 
                    SET end_time = ?, status = ?
                    WHERE id = ?
                """, (session.end_time.isoformat(), "completed", session_id))
                await db.commit()
            
            logger.info(f"✅ Scan session completed: {session_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار سیستم"""
        total_detections = len(self.detection_history)
        active_sessions = len([s for s in self.active_sessions.values() if s.status == "active"])
        
        miner_type_counts = {}
        for detection in self.detection_history:
            miner_type = detection.miner_type.value
            miner_type_counts[miner_type] = miner_type_counts.get(miner_type, 0) + 1
        
        return {
            "total_detections": total_detections,
            "active_sessions": active_sessions,
            "miner_type_distribution": miner_type_counts,
            "system_status": "operational"
        }

# Global core system instance
core_system = CoreSystem()

def get_core_system() -> CoreSystem:
    """دریافت instance سیستم اصلی"""
    return core_system

async def initialize_core():
    """راه‌اندازی سیستم اصلی"""
    await core_system.initialize_database()
    logger.info("🚀 Core system initialized successfully")
