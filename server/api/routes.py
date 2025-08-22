#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Secondary API Router - Additional API endpoints
روتر ثانویه API - نقاط پایانی اضافی API
"""

from fastapi import APIRouter, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime
import asyncio

# Import core modules
from ..core import get_core_system, ScanType, MinerType
from ..security import get_security_manager
from ..dashboard import get_dashboard_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# WebSocket connections
active_connections: List[WebSocket] = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial data
        dashboard_manager = get_dashboard_manager()
        await dashboard_manager.connect_websocket(websocket)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
                message = json.loads(data)
                logger.info(f"WebSocket message received: {message}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        await dashboard_manager.disconnect_websocket(websocket)

@router.get("/v2/status")
async def v2_status():
    """Version 2 status endpoint"""
    return {
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "advanced_detection",
            "real_time_monitoring",
            "geolocation",
            "owner_identification",
            "rf_analysis",
            "acoustic_detection",
            "thermal_analysis",
            "power_consumption_monitoring"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/v2/detections/recent")
async def get_recent_detections(limit: int = 20):
    """Get recent detections"""
    try:
        core_system = get_core_system()
        detections = await core_system.get_all_detections()
        
        # Get recent detections
        recent_detections = detections[:limit]
        
        detection_data = []
        for detection in recent_detections:
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
        logger.error(f"Failed to get recent detections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent detections"
        )

@router.get("/v2/alerts/recent")
async def get_recent_alerts(limit: int = 20):
    """Get recent alerts"""
    try:
        dashboard_manager = get_dashboard_manager()
        alerts = dashboard_manager.alerts[:limit]
        
        alert_data = []
        for alert in alerts:
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
        logger.error(f"Failed to get recent alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent alerts"
        )

@router.post("/v2/scan/start")
async def v2_start_scan(scan_data: Dict[str, Any]):
    """Start scan with advanced options"""
    try:
        core_system = get_core_system()
        
        scan_type = scan_data.get("scan_type", "network")
        target_range = scan_data.get("target_range", "192.168.1.0/24")
        options = scan_data.get("options", {})
        
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
        
        # Log scan start
        logger.info(f"Advanced scan started: {session_id} - Type: {scan_type} - Options: {options}")
        
        return {
            "session_id": session_id,
            "scan_type": scan_type,
            "target_range": target_range,
            "options": options,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to start advanced scan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scan"
        )

@router.post("/v2/scan/stop")
async def v2_stop_scan(session_id: str):
    """Stop scan session"""
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

@router.get("/v2/geolocation/{ip_address}")
async def get_geolocation(ip_address: str):
    """Get geolocation for IP address"""
    try:
        # Import geolocation service
        from ..services.geoip_lookup import get_geolocation_data
        
        location_data = await get_geolocation_data(ip_address)
        
        return {
            "ip_address": ip_address,
            "location": location_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get geolocation for {ip_address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get geolocation"
        )

@router.get("/v2/owner/{ip_address}")
async def get_owner_info(ip_address: str):
    """Get owner information for IP address"""
    try:
        # Import owner identification service
        from ..services.ownerIdentification import get_owner_details
        
        owner_data = await get_owner_details(ip_address)
        
        return {
            "ip_address": ip_address,
            "owner_info": owner_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get owner info for {ip_address}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get owner information"
        )

@router.post("/v2/rf/analyze")
async def analyze_rf_signals(rf_data: Dict[str, Any]):
    """Analyze RF signals"""
    try:
        # Import RF analyzer service
        from ..services.rfAnalyzer import analyze_rf_signature
        
        frequency_range = rf_data.get("frequency_range", "64-108 MHz")
        duration = rf_data.get("duration", 60)
        
        analysis_result = await analyze_rf_signature(frequency_range, duration)
        
        return {
            "analysis": analysis_result,
            "frequency_range": frequency_range,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze RF signals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze RF signals"
        )

@router.post("/v2/acoustic/analyze")
async def analyze_acoustic_signals(acoustic_data: Dict[str, Any]):
    """Analyze acoustic signals"""
    try:
        # Import acoustic detector service
        from ..services.acoustic_detector import analyze_acoustic_signature
        
        audio_file = acoustic_data.get("audio_file")
        duration = acoustic_data.get("duration", 30)
        
        analysis_result = await analyze_acoustic_signature(audio_file, duration)
        
        return {
            "analysis": analysis_result,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze acoustic signals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze acoustic signals"
        )

@router.post("/v2/thermal/analyze")
async def analyze_thermal_signals(thermal_data: Dict[str, Any]):
    """Analyze thermal signatures"""
    try:
        # Import thermal analyzer service
        from ..services.thermal_analyzer import analyze_thermal_signature
        
        thermal_image = thermal_data.get("thermal_image")
        temperature_range = thermal_data.get("temperature_range", "20-80°C")
        
        analysis_result = await analyze_thermal_signature(thermal_image, temperature_range)
        
        return {
            "analysis": analysis_result,
            "temperature_range": temperature_range,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze thermal signals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze thermal signals"
        )

@router.post("/v2/power/analyze")
async def analyze_power_consumption(power_data: Dict[str, Any]):
    """Analyze power consumption patterns"""
    try:
        # Import power analyzer service
        from ..services.power_analyzer import analyze_power_patterns
        
        power_readings = power_data.get("power_readings", [])
        time_period = power_data.get("time_period", "24h")
        
        analysis_result = await analyze_power_patterns(power_readings, time_period)
        
        return {
            "analysis": analysis_result,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze power consumption: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze power consumption"
        )

@router.get("/v2/export/detections")
async def export_detections(format: str = "json", date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Export detection data"""
    try:
        core_system = get_core_system()
        detections = await core_system.get_all_detections()
        
        # Filter by date range if specified
        if date_from and date_to:
            from_date = datetime.fromisoformat(date_from)
            to_date = datetime.fromisoformat(date_to)
            detections = [
                d for d in detections 
                if from_date <= d.timestamp <= to_date
            ]
        
        # Convert to export format
        export_data = []
        for detection in detections:
            export_data.append({
                "id": detection.id,
                "timestamp": detection.timestamp.isoformat(),
                "ip_address": detection.ip_address,
                "mac_address": detection.mac_address,
                "latitude": detection.location.get("lat", 0),
                "longitude": detection.location.get("lng", 0),
                "confidence": detection.confidence,
                "miner_type": detection.miner_type.value,
                "scan_type": detection.scan_type.value,
                "status": detection.status.value,
                "details": detection.details,
                "owner_info": detection.owner_info
            })
        
        if format.lower() == "csv":
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys() if export_data else [])
            writer.writeheader()
            writer.writerows(export_data)
            
            return JSONResponse(
                content={"csv_data": output.getvalue()},
                headers={"Content-Type": "text/csv"}
            )
        else:
            return {
                "format": format,
                "total_records": len(export_data),
                "data": export_data,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to export detections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export detections"
        )

@router.get("/v2/reports/summary")
async def get_summary_report(date_from: Optional[str] = None, date_to: Optional[str] = None):
    """Get summary report"""
    try:
        core_system = get_core_system()
        detections = await core_system.get_all_detections()
        
        # Filter by date range if specified
        if date_from and date_to:
            from_date = datetime.fromisoformat(date_from)
            to_date = datetime.fromisoformat(date_to)
            detections = [
                d for d in detections 
                if from_date <= d.timestamp <= to_date
            ]
        
        # Generate summary statistics
        total_detections = len(detections)
        miner_type_counts = {}
        scan_type_counts = {}
        confidence_ranges = {
            "high": 0,    # 80-100%
            "medium": 0,  # 50-79%
            "low": 0      # 0-49%
        }
        
        for detection in detections:
            # Count miner types
            miner_type = detection.miner_type.value
            miner_type_counts[miner_type] = miner_type_counts.get(miner_type, 0) + 1
            
            # Count scan types
            scan_type = detection.scan_type.value
            scan_type_counts[scan_type] = scan_type_counts.get(scan_type, 0) + 1
            
            # Count confidence ranges
            if detection.confidence >= 80:
                confidence_ranges["high"] += 1
            elif detection.confidence >= 50:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["low"] += 1
        
        return {
            "report_type": "summary",
            "date_range": {
                "from": date_from,
                "to": date_to
            },
            "statistics": {
                "total_detections": total_detections,
                "miner_type_distribution": miner_type_counts,
                "scan_type_distribution": scan_type_counts,
                "confidence_distribution": confidence_ranges
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate summary report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary report"
        )
