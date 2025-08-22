import psutil
import logging
from typing import List, Dict, Any
from datetime import datetime

class AdvancedMinerDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.miner_signatures = [
            "xmrig",
            "cgminer",
            "bfgminer",
            "ccminer",
            "ethminer",
            "phoenixminer",
            "nbminer",
            "teamredminer",
            "gminer",
            "lolminer"
        ]

    async def detect_miners(self) -> List[Dict[str, Any]]:
        """Detect potential cryptocurrency miners running on the system"""
        detected_miners = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                process_info = proc.info
                process_name = process_info['name'].lower()

                # Check against known miner signatures
                if any(miner in process_name for miner in self.miner_signatures):
                    miner_info = {
                        'pid': process_info['pid'],
                        'process_name': process_name,
                        'cpu_usage': process_info['cpu_percent'],
                        'memory_usage': process_info['memory_percent'],
                        'detection_time': datetime.now().isoformat(),
                        'detection_method': 'process_name_match',
                        'confidence_score': 90
                    }
                    detected_miners.append(miner_info)
                    continue

                # Check for high CPU usage
                if process_info['cpu_percent'] > 80:
                    miner_info = {
                        'pid': process_info['pid'],
                        'process_name': process_name,
                        'cpu_usage': process_info['cpu_percent'],
                        'memory_usage': process_info['memory_percent'],
                        'detection_time': datetime.now().isoformat(),
                        'detection_method': 'high_cpu_usage',
                        'confidence_score': 60
                    }
                    detected_miners.append(miner_info)

        except Exception as e:
            self.logger.error(f"Error during miner detection: {str(e)}")

        return detected_miners

    async def analyze_network_connections(self) -> List[Dict[str, Any]]:
        """Analyze network connections for mining pool patterns"""
        suspicious_connections = []

        try:
            connections = psutil.net_connections()
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    connection_info = {
                        'local_address': f"{conn.laddr[0]}:{conn.laddr[1]}",
                        'remote_address': f"{conn.raddr[0]}:{conn.raddr[1]}",
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    suspicious_connections.append(connection_info)

        except Exception as e:
            self.logger.error(f"Error analyzing network connections: {str(e)}")

        return suspicious_connections

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource usage metrics"""
        try:
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': dict(psutil.net_io_counters()._asdict()),
                'timestamp': datetime.now().isoformat()
            }
            return metrics

        except Exception as e:
            self.logger.error(f"Error getting system metrics: {str(e)}")
            return {}