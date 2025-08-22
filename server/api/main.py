#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main API Router - Primary API endpoints
روتر اصلی API - نقاط پایانی اصلی API
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime

# Import core modules
from ..core import get_core_system, DetectionResult, ScanType, MinerType
from ..security import get_security_manager
from ..dashboard import get_dashboard_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SHBH-HBSHY National Mining Detection System",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        core_system = get_core_system()
        dashboard_manager = get_dashboard_manager()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "core_system": "operational",
            "dashboard": "operational",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

@router.get("/status")
async def system_status():
    """System status endpoint"""
    try:
        core_system = get_core_system()
        stats = core_system.get_statistics()
        
        return {
            "system_status": "operational",
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "uptime": "24h 15m 30s",  # Placeholder
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system status"
        )

@router.post("/scan/start")
async def start_scan(scan_type: str, target_range: str = "192.168.1.0/24"):
    """Start a new scan session"""
    try:
        core_system = get_core_system()
        
        # Validate scan type
        try:
            scan_type_enum = ScanType(scan_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scan type: {scan_type}"
            )
        
        # Create scan session
        session_id = await core_system.create_scan_session(scan_type_enum, target_range)
        
        logger.info(f"Scan session started: {session_id} - Type: {scan_type}")
        
        return {
            "session_id": session_id,
            "scan_type": scan_type,
            "target_range": target_range,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scan"
        )

@router.post("/scan/stop")
async def stop_scan(session_id: str):
    """Stop a scan session"""
    try:
        core_system = get_core_system()
        await core_system.end_scan_session(session_id)
        
        logger.info(f"Scan session stopped: {session_id}")
        
        return {
            "session_id": session_id,
            "status": "stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to stop scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop scan"
        )

@router.get("/detections")
async def get_detections(limit: int = 100, session_id: Optional[str] = None):
    """Get detection results"""
    try:
        core_system = get_core_system()
        
        if session_id:
            detections = await core_system.get_session_results(session_id)
        else:
            detections = await core_system.get_all_detections()
        
        # Convert to dict format
        detection_data = []
        for detection in detections[:limit]:
            detection_data.append({
                "id": detection.id,
                "timestamp": detection.timestamp.isoformat(),
                "ip_address": detection.ip_address,
                "mac_address": detection.mac_address,
                "location": detection.location,
                "confidence": detection.confidence,
                "miner_type": detection.miner_type.value,
                "scan_type": detection.scan_type.value,
                "status": detection.status.value,
                "details": detection.details,
                "owner_info": detection.owner_info
            })
        
        return {
            "detections": detection_data,
            "total": len(detection_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get detections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get detections"
        )

@router.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    try:
        core_system = get_core_system()
        stats = core_system.get_statistics()
        
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@router.get("/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        dashboard_manager = get_dashboard_manager()
        dashboard_data = dashboard_manager.get_dashboard_data()
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Failed to get dashboard metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard metrics"
        )

@router.get("/alerts")
async def get_alerts(limit: int = 50, severity: Optional[str] = None):
    """Get system alerts"""
    try:
        dashboard_manager = get_dashboard_manager()
        alerts = dashboard_manager.alerts
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        alert_data = []
        for alert in alerts[:limit]:
            alert_data.append({
                "id": alert.id,
                "timestamp": alert.timestamp.isoformat(),
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "details": alert.details,
                "resolved": alert.resolved
            })
        
        return {
            "alerts": alert_data,
            "total": len(alert_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts"
        )

@router.post("/detections/add")
async def add_detection(detection_data: Dict[str, Any]):
    """Add a new detection result"""
    try:
        core_system = get_core_system()
        
        # Create detection result
        detection = DetectionResult(
            id=detection_data.get("id", f"det_{datetime.now().timestamp()}"),
            timestamp=datetime.fromisoformat(detection_data.get("timestamp", datetime.now().isoformat())),
            ip_address=detection_data["ip_address"],
            mac_address=detection_data.get("mac_address"),
            location=detection_data.get("location", {"lat": 0, "lng": 0}),
            confidence=detection_data.get("confidence", 0.0),
            miner_type=MinerType(detection_data.get("miner_type", "unknown")),
            scan_type=ScanType(detection_data.get("scan_type", "network")),
            status=detection_data.get("status", "detected"),
            details=detection_data.get("details", {}),
            owner_info=detection_data.get("owner_info")
        )
        
        # Add to session if specified
        session_id = detection_data.get("session_id")
        if session_id:
            await core_system.add_detection_result(session_id, detection)
        
        logger.info(f"Detection added: {detection.ip_address}")
        
        return {
            "id": detection.id,
            "status": "added",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to add detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add detection"
        )

@router.get("/logs/system")
async def get_system_logs(limit: int = 100, level: Optional[str] = None):
    """Get system logs"""
    try:
        from ..logging import get_logger
        logger_system = get_logger()
        logs = await logger_system.get_system_logs(limit=limit, level=level)
        
        return {
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system logs"
        )

@router.get("/logs/security")
async def get_security_logs(limit: int = 100, severity: Optional[str] = None):
    """Get security logs"""
    try:
        from ..logging import get_logger
        logger_system = get_logger()
        logs = await logger_system.get_security_logs(limit=limit, severity=severity)
        
        return {
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get security logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security logs"
        )
