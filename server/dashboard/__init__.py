#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Module - Real-time Monitoring and Control Interface
ماژول داشبورد - رابط نظارت و کنترل زمان واقعی
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiosqlite
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DashboardMetrics:
    """معیارهای داشبورد"""
    total_detections: int
    active_scans: int
    system_status: str
    last_scan_time: Optional[datetime]
    detection_rate: float
    false_positive_rate: float
    coverage_percentage: float

@dataclass
class Alert:
    """هشدار"""
    id: str
    timestamp: datetime
    type: str
    severity: str
    message: str
    details: Dict[str, Any]
    resolved: bool = False

class DashboardManager:
    """
    مدیر داشبورد برای نظارت و کنترل سیستم
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.active_connections: List[WebSocket] = []
        self.alerts: List[Alert] = []
        self.metrics: Optional[DashboardMetrics] = None
        
    async def initialize(self):
        """راه‌اندازی داشبورد"""
        await self._load_alerts()
        await self._update_metrics()
        logger.info("📊 Dashboard initialized successfully")
    
    async def _load_alerts(self):
        """بارگذاری هشدارها از پایگاه داده"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT id, timestamp, type, severity, message, details, resolved
                    FROM alerts ORDER BY timestamp DESC LIMIT 100
                """) as cursor:
                    rows = await cursor.fetchall()
                    self.alerts = [
                        Alert(
                            id=row[0],
                            timestamp=datetime.fromisoformat(row[1]),
                            type=row[2],
                            severity=row[3],
                            message=row[4],
                            details=json.loads(row[5]),
                            resolved=bool(row[6])
                        )
                        for row in rows
                    ]
        except Exception as e:
            logger.error(f"Failed to load alerts: {e}")
            self.alerts = []
    
    async def _update_metrics(self):
        """به‌روزرسانی معیارهای داشبورد"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total detections
                async with db.execute("SELECT COUNT(*) FROM detection_results") as cursor:
                    total_detections = (await cursor.fetchone())[0]
                
                # Active scans
                async with db.execute("SELECT COUNT(*) FROM scan_sessions WHERE status = 'active'") as cursor:
                    active_scans = (await cursor.fetchone())[0]
                
                # Last scan time
                async with db.execute("SELECT MAX(start_time) FROM scan_sessions") as cursor:
                    last_scan_row = await cursor.fetchone()
                    last_scan_time = datetime.fromisoformat(last_scan_row[0]) if last_scan_row[0] else None
                
                # Detection rate (last 24 hours)
                yesterday = datetime.now() - timedelta(days=1)
                async with db.execute("""
                    SELECT COUNT(*) FROM detection_results 
                    WHERE timestamp > ?
                """, (yesterday.isoformat(),)) as cursor:
                    recent_detections = (await cursor.fetchone())[0]
                
                detection_rate = recent_detections / 24.0 if recent_detections > 0 else 0.0
                
                self.metrics = DashboardMetrics(
                    total_detections=total_detections,
                    active_scans=active_scans,
                    system_status="operational",
                    last_scan_time=last_scan_time,
                    detection_rate=detection_rate,
                    false_positive_rate=0.05,  # Placeholder
                    coverage_percentage=85.0   # Placeholder
                )
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            self.metrics = DashboardMetrics(
                total_detections=0,
                active_scans=0,
                system_status="error",
                last_scan_time=None,
                detection_rate=0.0,
                false_positive_rate=0.0,
                coverage_percentage=0.0
            )
    
    async def add_alert(self, alert: Alert):
        """افزودن هشدار جدید"""
        self.alerts.insert(0, alert)
        
        # Save to database
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO alerts (id, timestamp, type, severity, message, details, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.id,
                    alert.timestamp.isoformat(),
                    alert.type,
                    alert.severity,
                    alert.message,
                    json.dumps(alert.details),
                    alert.resolved
                ))
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
        
        # Broadcast to connected clients
        await self._broadcast_alert(alert)
    
    async def connect_websocket(self, websocket: WebSocket):
        """اتصال WebSocket جدید"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send current state
        await websocket.send_text(json.dumps({
            "type": "initial_state",
            "metrics": asdict(self.metrics) if self.metrics else {},
            "alerts": [asdict(alert) for alert in self.alerts[:10]]
        }))
        
        logger.info(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect_websocket(self, websocket: WebSocket):
        """قطع اتصال WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def _broadcast_alert(self, alert: Alert):
        """ارسال هشدار به تمام اتصالات فعال"""
        message = json.dumps({
            "type": "new_alert",
            "alert": asdict(alert)
        })
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            await self.disconnect_websocket(connection)
    
    async def broadcast_metrics_update(self):
        """ارسال به‌روزرسانی معیارها"""
        await self._update_metrics()
        
        message = json.dumps({
            "type": "metrics_update",
            "metrics": asdict(self.metrics) if self.metrics else {}
        })
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Failed to send metrics update: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            await self.disconnect_websocket(connection)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """دریافت داده‌های داشبورد"""
        return {
            "metrics": asdict(self.metrics) if self.metrics else {},
            "alerts": [asdict(alert) for alert in self.alerts[:20]],
            "active_connections": len(self.active_connections),
            "system_uptime": "24h 15m 30s",  # Placeholder
            "last_update": datetime.now().isoformat()
        }

# Global dashboard manager instance
dashboard_manager = DashboardManager()

def get_dashboard_manager() -> DashboardManager:
    """دریافت instance مدیر داشبورد"""
    return dashboard_manager

async def initialize_dashboard():
    """راه‌اندازی داشبورد"""
    await dashboard_manager.initialize()
    logger.info("📊 Dashboard system initialized successfully")
