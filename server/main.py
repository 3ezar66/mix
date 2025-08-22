"""
Main FastAPI Application
"""
from datetime import datetime
import psutil
import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Any

from core.config import config
from services.network_scanner import NetworkScanner
from services.miner_detector import AdvancedMinerDetector
from services.geoip_lookup import GeoIPLookup
from security.auth import get_current_user, create_access_token
from log_utils import get_logger

# Initialize logger
logger = get_logger()

app = FastAPI(
    title=config["project_name"],
    version=config["version"]
)

# CORS middleware with enhanced security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)

# Initialize services
scanner = NetworkScanner()
detector = AdvancedMinerDetector()
geo_lookup = GeoIPLookup()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get access token"""
    token = create_access_token(form_data.username)
    await logger.log_security_event(
        event_type="login",
        user_id=form_data.username,
        ip_address="127.0.0.1",  # TODO: Get actual IP
        action="token_generated",
        details={"token_type": "bearer"},
        severity="info"
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/scan/{network}")
async def scan_network(
    network: str,
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Scan network for devices"""
    try:
        await logger.log_system_event(
            level="info",
            module="network_scanner",
            message=f"Starting network scan for {network}",
            user_id=current_user.get('id')
        )
        
        devices = scanner.scan_network(network)
        for device in devices:
            # Enrich with geolocation
            device['location'] = geo_lookup.lookup(device['ip_address'])
            # Check for miner signatures
            if device.get('open_ports'):
                device['miner_detection'] = detector.detect_miner_signatures(
                    device['ip_address'],
                    device['open_ports']
                )
                
                if device['miner_detection'].get('is_miner'):
                    await logger.log_detection_event(
                        detection_id=str(uuid.uuid4()),
                        ip_address=device['ip_address'],
                        miner_type=device['miner_detection'].get('miner_type', 'unknown'),
                        confidence=device['miner_detection'].get('confidence', 0.0),
                        scan_type='network_scan',
                        details=device
                    )
        
        return devices
    except Exception as e:
        await logger.log_system_event(
            level="error",
            module="network_scanner",
            message=f"Error scanning network {network}: {str(e)}",
            user_id=current_user.get('id')
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/device/{ip}")
async def get_device_info(
    ip: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed device information"""
    try:
        device = scanner._scan_host(ip)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Enrich with additional data
        device['location'] = geo_lookup.lookup(ip)
        device['miner_detection'] = detector.detect_miner_signatures(
            ip,
            device.get('open_ports', [])
        )
        
        return device
    except HTTPException:
        raise
    except Exception as e:
        await logger.log_system_event(
            level="error",
            module="device_info",
            message=f"Error getting device info for {ip}: {str(e)}",
            user_id=current_user.get('id')
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/stats")
async def get_statistics(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive system statistics"""
    try:
        # Get scan statistics
        total_devices = len(scanner.get_all_devices())
        detected_miners = len(detector.get_detected_miners())
        recent_scans = scanner.get_recent_scans(limit=10)
        
        # Calculate success rate
        success_rate = scanner.calculate_scan_success_rate()
        
        # Get system health metrics
        system_health = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
        stats = {
            "status": "operational",
            "version": config["version"],
            "statistics": {
                "total_devices": total_devices,
                "detected_miners": detected_miners,
                "success_rate": success_rate,
                "recent_scans": recent_scans
            },
            "system_health": system_health,
            "last_update": datetime.now().isoformat()
        }
        
        await logger.log_system_event(
            level="info",
            module="statistics",
            message="Statistics retrieved successfully",
            user_id=current_user.get('id'),
            details=stats
        )
        
        return stats
    except Exception as e:
        await logger.log_system_event(
            level="error",
            module="statistics",
            message=f"Error fetching statistics: {str(e)}",
            user_id=current_user.get('id')
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )
