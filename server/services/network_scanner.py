"""
Network scanning and device discovery utilities
"""
import socket
import ipaddress
import concurrent.futures
from typing import List, Dict, Any
from scapy.all import ARP, Ether, srp
import logging
import json
from datetime import datetime
import time
import platform
import subprocess
from ratelimit import limits, sleep_and_retry

from core.config import config
from core.database import get_session, Device, ScanResult

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __enter__(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.calls.append(now)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class NetworkScanner:
    def __init__(self):
        self.config = config['scan']
        
    def scan_network(self, network: str) -> List[Dict[str, Any]]:
        """Enhanced network scanning with rate limiting and progress tracking"""
        try:
            net = ipaddress.ip_network(network)
            devices = []
            total_hosts = sum(1 for _ in net.hosts())
            scanned_hosts = 0
            start_time = time.time()
            
            # Configure rate limiting
            max_workers = min(50, total_hosts)
            rate_limit = RateLimiter(max_calls=100, period=1)  # 100 scans per second
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for ip in net.hosts():
                    with rate_limit:
                        futures.append(executor.submit(self._scan_host, str(ip)))
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            devices.append(result)
                            self._save_device(result)
                    except Exception as e:
                        logger.error(f"Error scanning host: {e}")
                    
                    scanned_hosts += 1
                    if scanned_hosts % 10 == 0:  # Log progress every 10 hosts
                        progress = (scanned_hosts / total_hosts) * 100
                        elapsed = time.time() - start_time
                        rate = scanned_hosts / elapsed if elapsed > 0 else 0
                        logger.info(f"Progress: {progress:.1f}% ({scanned_hosts}/{total_hosts}) - Rate: {rate:.1f} hosts/sec")
            
            scan_time = time.time() - start_time
            logger.info(f"Scan completed in {scan_time:.1f} seconds. Found {len(devices)} devices")
            return devices
            
        except Exception as e:
            logger.error(f"Network scan error: {e}")
            return []
    
    def _scan_host(self, ip: str) -> Dict[str, Any]:
        """Scan a single host for basic information"""
        try:
            # Check if host is up
            if not self._ping_host(ip):
                return None
                
            # Get MAC address
            mac = self._get_mac(ip)
            if not mac:
                return None
                
            # Basic device info
            device = {
                'ip_address': ip,
                'mac_address': mac,
                'hostname': self._get_hostname(ip),
                'open_ports': self._scan_ports(ip),
                'scan_time': datetime.utcnow()
            }
            
            return device
            
        except Exception as e:
            logger.debug(f"Host scan error ({ip}): {e}")
            return None
    
    def _ping_host(self, ip: str) -> bool:
        """Enhanced host availability check using multiple methods"""
        # Try ICMP ping first (requires root/admin)
        try:
            if platform.system().lower() == "windows":
                response = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            else:
                response = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            if response.returncode == 0:
                return True
        except:
            pass

        # Try common ports as fallback
        common_ports = [80, 443, 22, 445, 3389, 8080, 8443]
        for port in common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect((ip, port))
                    return True
            except:
                continue
        return False
    
    def _get_mac(self, ip: str) -> str:
        """Get MAC address using ARP"""
        try:
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip),
                timeout=2,
                verbose=False
            )
            if ans:
                return ans[0][1].hwsrc
        except Exception as e:
            logger.debug(f"MAC lookup error ({ip}): {e}")
        return None
    
    def _get_hostname(self, ip: str) -> str:
        """Get hostname using reverse DNS"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return None
    
    def _scan_ports(self, ip: str) -> List[Dict[str, Any]]:
        """Enhanced port scanning with service detection"""
        open_ports = []
        # Extended port list including common miner ports
        common_ports = [
            21, 22, 80, 443, 3389, 8080, 8443,  # Common services
            3333, 4444, 5555, 7777, 9999,  # Common miner ports
            1433, 3306, 5432,  # Database ports
            6666, 8888, 14444, 14433  # Additional miner ports
        ]
        
        for port in common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        # Try to identify service
                        service = self._identify_service(ip, port)
                        open_ports.append({
                            'port': port,
                            'service': service,
                            'last_seen': datetime.now().isoformat()
                        })
            except Exception as e:
                logging.debug(f"Error scanning port {port} on {ip}: {str(e)}")
                continue
        
        return open_ports
    
    def _save_device(self, device_data: Dict[str, Any]):
        """Save device to database"""
        try:
            session = get_session()
            
            # Check if device exists
            device = session.query(Device).filter_by(
                ip_address=device_data['ip_address']
            ).first()
            
            if device:
                # Update existing device
                device.last_seen = device_data['scan_time']
                device.mac_address = device_data['mac_address']
                device.hostname = device_data['hostname']
            else:
                # Create new device
                device = Device(
                    ip_address=device_data['ip_address'],
                    mac_address=device_data['mac_address'],
                    hostname=device_data['hostname'],
                    first_seen=device_data['scan_time'],
                    last_seen=device_data['scan_time']
                )
                session.add(device)
            
            # Add scan result
            scan_result = ScanResult(
                device_id=device.id,
                scan_time=device_data['scan_time'],
                open_ports=device_data['open_ports'],
                raw_data=device_data
            )
            session.add(scan_result)
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            session.rollback()
        finally:
            session.close()

# Example usage
if __name__ == "__main__":
    scanner = NetworkScanner()
    results = scanner.scan_network("192.168.1.0/24")
    print(json.dumps(results, indent=2, default=str))
