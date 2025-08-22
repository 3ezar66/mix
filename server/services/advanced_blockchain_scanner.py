#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Blockchain and Cryptocurrency Mining Scanner
اسکنر پیشرفته بلاکچین و استخراج رمزارز
"""

import asyncio
import subprocess
import socket
import struct
import time
import json
import logging
import ipaddress
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import nmap
import pyshark
from scapy.all import *
import requests
import aiohttp
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BlockchainDetection:
    """نتیجه تشخیص بلاکچین"""
    ip_address: str
    port: int
    protocol: str
    blockchain_type: str
    confidence: float
    timestamp: datetime
    details: Dict[str, Any]
    vpn_detected: bool = False
    proxy_detected: bool = False
    geolocation: Optional[Dict[str, Any]] = None

class AdvancedBlockchainScanner:
    """
    اسکنر پیشرفته بلاکچین برای تشخیص ماینرهای رمزارز
    حتی در صورت استفاده از VPN و Proxy
    """
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.blockchain_ports = {
            # Bitcoin
            'bitcoin': [8333, 8332, 18333, 18444, 8334, 8335],
            # Ethereum
            'ethereum': [30303, 8545, 8546, 30304, 30305],
            # Monero
            'monero': [18080, 18081, 18082, 18083, 18084],
            # Litecoin
            'litecoin': [9333, 9332, 19333, 19444],
            # Dash
            'dash': [9999, 9998, 19999, 19998],
            # Zcash
            'zcash': [8233, 8232, 18233, 18232],
            # Stratum Mining Pools
            'stratum': [3333, 3334, 3335, 3336, 3337, 3338, 3339],
            # Pool Mining
            'pool_mining': [4028, 4029, 4030, 8080, 8888, 8889, 8890],
            # Other Cryptocurrencies
            'other_crypto': [9333, 9334, 9335, 9336, 9337, 9338, 9339]
        }
        
        self.vpn_providers = [
            'nordvpn', 'expressvpn', 'surfshark', 'cyberghost', 'protonvpn',
            'private internet access', 'tunnelbear', 'windscribe', 'mullvad',
            'ivpn', 'perfect privacy', 'airvpn', 'hide.me', 'vpn.ac'
        ]
        
        self.proxy_indicators = [
            'proxy', 'socks', 'tor', 'vpn', 'tunnel', 'gateway'
        ]
    
    async def scan_global_blockchain_network(self, target_ranges: List[str] = None) -> List[BlockchainDetection]:
        """
        اسکن شبکه جهانی بلاکچین برای یافتن ماینرها
        """
        detections = []
        
        if not target_ranges:
            # اسکن محدوده‌های جهانی مهم
            target_ranges = [
                "0.0.0.0/0",  # تمام IP ها (با محدودیت)
                "10.0.0.0/8",
                "172.16.0.0/12", 
                "192.168.0.0/16",
                "100.64.0.0/10",  # Carrier-grade NAT
                "169.254.0.0/16"  # Link-local
            ]
        
        for target_range in target_ranges:
            logger.info(f"🔍 Scanning blockchain network: {target_range}")
            
            try:
                # اسکن پورت‌های بلاکچین
                blockchain_detections = await self._scan_blockchain_ports(target_range)
                detections.extend(blockchain_detections)
                
                # تحلیل ترافیک بلاکچین
                traffic_detections = await self._analyze_blockchain_traffic(target_range)
                detections.extend(traffic_detections)
                
                # تشخیص VPN/Proxy
                vpn_detections = await self._detect_vpn_proxy_usage(target_range)
                detections.extend(vpn_detections)
                
            except Exception as e:
                logger.error(f"Error scanning {target_range}: {e}")
        
        return detections
    
    async def _scan_blockchain_ports(self, target_range: str) -> List[BlockchainDetection]:
        """
        اسکن پورت‌های منحصربفرد بلاکچین
        """
        detections = []
        
        try:
            # استفاده از Nmap برای اسکن سریع
            scan_args = [
                '-sS',  # SYN scan
                '-sU',  # UDP scan
                '--top-ports', '1000',
                '--script', 'banner',
                '--script-args', 'banner.maxlen=1000',
                '--max-retries', '2',
                '--host-timeout', '30s'
            ]
            
            # اضافه کردن پورت‌های بلاکچین
            blockchain_ports = []
            for ports in self.blockchain_ports.values():
                blockchain_ports.extend(ports)
            
            scan_args.extend(['-p', ','.join(map(str, blockchain_ports))])
            
            logger.info(f"Scanning blockchain ports: {target_range}")
            result = self.nm.scan(hosts=target_range, arguments=' '.join(scan_args))
            
            for host in result['scan']:
                if 'tcp' in result['scan'][host]:
                    for port in result['scan'][host]['tcp']:
                        if result['scan'][host]['tcp'][port]['state'] == 'open':
                            detection = await self._analyze_blockchain_port(host, port, result['scan'][host]['tcp'][port])
                            if detection:
                                detections.append(detection)
                
                if 'udp' in result['scan'][host]:
                    for port in result['scan'][host]['udp']:
                        if result['scan'][host]['udp'][port]['state'] == 'open':
                            detection = await self._analyze_blockchain_port(host, port, result['scan'][host]['udp'][port])
                            if detection:
                                detections.append(detection)
                                
        except Exception as e:
            logger.error(f"Error in blockchain port scan: {e}")
        
        return detections
    
    async def _analyze_blockchain_port(self, host: str, port: int, port_info: Dict) -> Optional[BlockchainDetection]:
        """
        تحلیل پورت بلاکچین
        """
        try:
            # تشخیص نوع بلاکچین بر اساس پورت
            blockchain_type = self._identify_blockchain_type(port)
            
            if not blockchain_type:
                return None
            
            # تست اتصال مستقیم
            connection_details = await self._test_blockchain_connection(host, port)
            
            # تشخیص VPN/Proxy
            vpn_detected, proxy_detected = await self._check_vpn_proxy(host)
            
            # تعیین موقعیت جغرافیایی
            geolocation = await self._get_geolocation(host)
            
            detection = BlockchainDetection(
                ip_address=host,
                port=port,
                protocol=port_info.get('name', 'unknown'),
                blockchain_type=blockchain_type,
                confidence=connection_details.get('confidence', 0.5),
                timestamp=datetime.now(),
                details={
                    'banner': port_info.get('script', {}).get('banner', ''),
                    'connection_test': connection_details,
                    'port_info': port_info
                },
                vpn_detected=vpn_detected,
                proxy_detected=proxy_detected,
                geolocation=geolocation
            )
            
            logger.info(f"🎯 Blockchain detection: {host}:{port} - {blockchain_type}")
            return detection
            
        except Exception as e:
            logger.error(f"Error analyzing blockchain port {host}:{port}: {e}")
            return None
    
    def _identify_blockchain_type(self, port: int) -> Optional[str]:
        """
        شناسایی نوع بلاکچین بر اساس پورت
        """
        for blockchain_type, ports in self.blockchain_ports.items():
            if port in ports:
                return blockchain_type
        return None
    
    async def _test_blockchain_connection(self, host: str, port: int) -> Dict[str, Any]:
        """
        تست اتصال بلاکچین
        """
        try:
            # تست اتصال TCP
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=10.0
            )
            
            # ارسال درخواست بلاکچین
            blockchain_requests = [
                b'{"jsonrpc": "2.0", "method": "getblockchaininfo", "params": [], "id": 1}\n',
                b'{"jsonrpc": "2.0", "method": "getinfo", "params": [], "id": 1}\n',
                b'{"method": "eth_blockNumber", "params": [], "id": 1, "jsonrpc": "2.0"}\n'
            ]
            
            responses = []
            for request in blockchain_requests:
                try:
                    writer.write(request)
                    await writer.drain()
                    
                    response = await asyncio.wait_for(reader.read(1024), timeout=5.0)
                    responses.append(response.decode('utf-8', errors='ignore'))
                except:
                    continue
            
            writer.close()
            await writer.wait_closed()
            
            # تحلیل پاسخ‌ها
            confidence = 0.0
            if responses:
                for response in responses:
                    if any(keyword in response.lower() for keyword in ['blockchain', 'bitcoin', 'ethereum', 'block', 'hash']):
                        confidence += 0.3
                    if 'jsonrpc' in response.lower():
                        confidence += 0.2
                    if 'result' in response.lower():
                        confidence += 0.2
            
            return {
                'connected': True,
                'responses': responses,
                'confidence': min(confidence, 1.0)
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'confidence': 0.0
            }
    
    async def _detect_vpn_proxy_usage(self, target_range: str) -> List[BlockchainDetection]:
        """
        تشخیص استفاده از VPN و Proxy
        """
        detections = []
        
        try:
            # اسکن برای پورت‌های VPN/Proxy
            vpn_proxy_ports = [1080, 3128, 8080, 8118, 9050, 9150, 10808, 10809]
            
            scan_args = [
                '-sS',
                '-p', ','.join(map(str, vpn_proxy_ports)),
                '--script', 'http-title,http-headers',
                '--max-retries', '2'
            ]
            
            result = self.nm.scan(hosts=target_range, arguments=' '.join(scan_args))
            
            for host in result['scan']:
                if 'tcp' in result['scan'][host]:
                    for port in result['scan'][host]['tcp']:
                        if result['scan'][host]['tcp'][port]['state'] == 'open':
                            vpn_detected, proxy_detected = await self._check_vpn_proxy(host)
                            
                            if vpn_detected or proxy_detected:
                                detection = BlockchainDetection(
                                    ip_address=host,
                                    port=port,
                                    protocol='vpn_proxy',
                                    blockchain_type='potential_miner',
                                    confidence=0.8,
                                    timestamp=datetime.now(),
                                    details={
                                        'vpn_detected': vpn_detected,
                                        'proxy_detected': proxy_detected,
                                        'port_info': result['scan'][host]['tcp'][port]
                                    },
                                    vpn_detected=vpn_detected,
                                    proxy_detected=proxy_detected
                                )
                                detections.append(detection)
                                
        except Exception as e:
            logger.error(f"Error detecting VPN/Proxy: {e}")
        
        return detections
    
    async def _check_vpn_proxy(self, host: str) -> Tuple[bool, bool]:
        """
        بررسی استفاده از VPN یا Proxy
        """
        try:
            # بررسی DNS
            dns_info = await self._check_dns_characteristics(host)
            
            # بررسی WHOIS
            whois_info = await self._check_whois_characteristics(host)
            
            # بررسی ASN
            asn_info = await self._check_asn_characteristics(host)
            
            # تشخیص VPN
            vpn_indicators = 0
            if dns_info.get('vpn_likely'):
                vpn_indicators += 1
            if whois_info.get('vpn_likely'):
                vpn_indicators += 1
            if asn_info.get('vpn_likely'):
                vpn_indicators += 1
            
            vpn_detected = vpn_indicators >= 2
            
            # تشخیص Proxy
            proxy_indicators = 0
            if dns_info.get('proxy_likely'):
                proxy_indicators += 1
            if whois_info.get('proxy_likely'):
                proxy_indicators += 1
            if asn_info.get('proxy_likely'):
                proxy_indicators += 1
            
            proxy_detected = proxy_indicators >= 2
            
            return vpn_detected, proxy_detected
            
        except Exception as e:
            logger.error(f"Error checking VPN/Proxy for {host}: {e}")
            return False, False
    
    async def _check_dns_characteristics(self, host: str) -> Dict[str, Any]:
        """
        بررسی ویژگی‌های DNS برای تشخیص VPN/Proxy
        """
        try:
            # بررسی DNS PTR record
            try:
                hostname = socket.gethostbyaddr(host)[0]
                
                vpn_likely = any(provider in hostname.lower() for provider in self.vpn_providers)
                proxy_likely = any(indicator in hostname.lower() for indicator in self.proxy_indicators)
                
                return {
                    'hostname': hostname,
                    'vpn_likely': vpn_likely,
                    'proxy_likely': proxy_likely
                }
            except:
                return {
                    'hostname': None,
                    'vpn_likely': False,
                    'proxy_likely': False
                }
                
        except Exception as e:
            logger.error(f"Error checking DNS characteristics: {e}")
            return {'vpn_likely': False, 'proxy_likely': False}
    
    async def _check_whois_characteristics(self, host: str) -> Dict[str, Any]:
        """
        بررسی ویژگی‌های WHOIS برای تشخیص VPN/Proxy
        """
        try:
            # استفاده از API رایگان WHOIS
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://ip-api.com/json/{host}') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # بررسی ISP
                        isp = data.get('isp', '').lower()
                        org = data.get('org', '').lower()
                        
                        vpn_likely = any(provider in isp or provider in org for provider in self.vpn_providers)
                        proxy_likely = any(indicator in isp or indicator in org for indicator in self.proxy_indicators)
                        
                        return {
                            'isp': isp,
                            'org': org,
                            'vpn_likely': vpn_likely,
                            'proxy_likely': proxy_likely
                        }
            
            return {'vpn_likely': False, 'proxy_likely': False}
            
        except Exception as e:
            logger.error(f"Error checking WHOIS characteristics: {e}")
            return {'vpn_likely': False, 'proxy_likely': False}
    
    async def _check_asn_characteristics(self, host: str) -> Dict[str, Any]:
        """
        بررسی ویژگی‌های ASN برای تشخیص VPN/Proxy
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://ip-api.com/json/{host}') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        asn = data.get('as', '').lower()
                        
                        vpn_likely = any(provider in asn for provider in self.vpn_providers)
                        proxy_likely = any(indicator in asn for indicator in self.proxy_indicators)
                        
                        return {
                            'asn': asn,
                            'vpn_likely': vpn_likely,
                            'proxy_likely': proxy_likely
                        }
            
            return {'vpn_likely': False, 'proxy_likely': False}
            
        except Exception as e:
            logger.error(f"Error checking ASN characteristics: {e}")
            return {'vpn_likely': False, 'proxy_likely': False}
    
    async def _analyze_blockchain_traffic(self, target_range: str) -> List[BlockchainDetection]:
        """
        تحلیل ترافیک بلاکچین با Wireshark
        """
        detections = []
        
        try:
            # استفاده از PyShark برای تحلیل ترافیک
            capture = pyshark.LiveCapture(interface='any')
            capture.set_debug()
            
            # فیلتر برای ترافیک بلاکچین
            blockchain_filters = [
                'tcp.port == 8333 or tcp.port == 30303 or tcp.port == 18080',
                'tcp.port == 3333 or tcp.port == 4028 or tcp.port == 8080',
                'tcp contains "bitcoin" or tcp contains "ethereum"',
                'tcp contains "blockchain" or tcp contains "mining"'
            ]
            
            for filter_expr in blockchain_filters:
                try:
                    capture.apply_on_packets(self._process_blockchain_packet, display_filter=filter_expr)
                except Exception as e:
                    logger.error(f"Error applying filter {filter_expr}: {e}")
            
            capture.close()
            
        except Exception as e:
            logger.error(f"Error analyzing blockchain traffic: {e}")
        
        return detections
    
    def _process_blockchain_packet(self, packet):
        """
        پردازش پکت بلاکچین
        """
        try:
            if hasattr(packet, 'ip'):
                detection = BlockchainDetection(
                    ip_address=packet.ip.src,
                    port=int(packet.tcp.srcport),
                    protocol='blockchain_traffic',
                    blockchain_type='detected_from_traffic',
                    confidence=0.7,
                    timestamp=datetime.now(),
                    details={
                        'packet_length': len(packet),
                        'protocol': packet.transport_layer,
                        'payload_preview': str(packet)[:200]
                    }
                )
                
                logger.info(f"🎯 Blockchain traffic detected: {packet.ip.src}:{packet.tcp.srcport}")
                
        except Exception as e:
            logger.error(f"Error processing blockchain packet: {e}")
    
    async def _get_geolocation(self, host: str) -> Optional[Dict[str, Any]]:
        """
        دریافت موقعیت جغرافیایی
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://ip-api.com/json/{host}') as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'country': data.get('country'),
                            'region': data.get('regionName'),
                            'city': data.get('city'),
                            'lat': data.get('lat'),
                            'lon': data.get('lon'),
                            'isp': data.get('isp'),
                            'org': data.get('org')
                        }
            return None
            
        except Exception as e:
            logger.error(f"Error getting geolocation for {host}: {e}")
            return None
    
    async def start_continuous_monitoring(self, target_ranges: List[str] = None):
        """
        شروع نظارت مداوم
        """
        logger.info("🚀 Starting continuous blockchain monitoring...")
        
        while True:
            try:
                detections = await self.scan_global_blockchain_network(target_ranges)
                
                # ذخیره نتایج
                await self._save_detections(detections)
                
                # گزارش نتایج
                logger.info(f"📊 Found {len(detections)} blockchain activities")
                
                # انتظار قبل از اسکن بعدی
                await asyncio.sleep(300)  # 5 دقیقه
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)
    
    async def _save_detections(self, detections: List[BlockchainDetection]):
        """
        ذخیره نتایج تشخیص
        """
        try:
            async with aiofiles.open('blockchain_detections.json', 'a') as f:
                for detection in detections:
                    detection_data = {
                        'ip_address': detection.ip_address,
                        'port': detection.port,
                        'blockchain_type': detection.blockchain_type,
                        'confidence': detection.confidence,
                        'timestamp': detection.timestamp.isoformat(),
                        'vpn_detected': detection.vpn_detected,
                        'proxy_detected': detection.proxy_detected,
                        'geolocation': detection.geolocation,
                        'details': detection.details
                    }
                    await f.write(json.dumps(detection_data) + '\n')
                    
        except Exception as e:
            logger.error(f"Error saving detections: {e}")

# Global scanner instance
blockchain_scanner = AdvancedBlockchainScanner()

async def main():
    """
    تابع اصلی برای اجرای اسکنر
    """
    logger.info("🔍 Starting Advanced Blockchain Scanner...")
    
    # اسکن اولیه
    detections = await blockchain_scanner.scan_global_blockchain_network()
    
    logger.info(f"🎯 Found {len(detections)} blockchain activities")
    
    # شروع نظارت مداوم
    await blockchain_scanner.start_continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 