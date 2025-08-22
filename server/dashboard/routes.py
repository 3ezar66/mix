"""
Dashboard API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..core.database import get_session, Device, ScanResult
from ..security.auth import get_current_user

router = APIRouter()

@router.get("/overview")
async def get_overview(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard overview statistics"""
    session = get_session()
    try:
        total_devices = session.query(Device).count()
        miners = session.query(Device).filter(Device.is_miner == True).count()
        suspicious = session.query(Device).filter(
            Device.confidence_score >= 40,
            Device.confidence_score < 70
        ).count()
        
        # Recent scans
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_scans = session.query(ScanResult).filter(
            ScanResult.scan_time >= recent_cutoff
        ).count()
        
        return {
            "total_devices": total_devices,
            "confirmed_miners": miners,
            "suspicious_devices": suspicious,
            "scans_24h": recent_scans,
            "timestamp": datetime.utcnow()
        }
    finally:
        session.close()

@router.get("/miners")
async def get_miners(
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get list of confirmed miners"""
    session = get_session()
    try:
        miners = session.query(Device).filter(
            Device.is_miner == True
        ).all()
        
        return [{
            "id": m.id,
            "ip_address": m.ip_address,
            "hostname": m.hostname,
            "first_seen": m.first_seen,
            "last_seen": m.last_seen,
            "confidence_score": m.confidence_score,
            "detection_methods": m.detection_methods,
            "location": m.location_data,
            "owner": m.owner_info
        } for m in miners]
    finally:
        session.close()

@router.get("/activity")
async def get_activity(
    hours: int = 24,
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get recent scanning activity"""
    session = get_session()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        activity = session.query(ScanResult).filter(
            ScanResult.scan_time >= cutoff
        ).all()
        
        return [{
            "id": a.id,
            "device_id": a.device_id,
            "scan_time": a.scan_time,
            "open_ports": a.open_ports,
            "services": a.services,
            "hash_rate": a.hash_rate,
            "power_consumption": a.power_consumption
        } for a in activity]
    finally:
        session.close()
