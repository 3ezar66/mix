#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wireshark-based Cryptocurrency Mining Traffic Analyzer
تحلیلگر ترافیک ماینینگ رمزارز با استفاده از Wireshark
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import pyshark
import subprocess
import os
import re
from scapy.all import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MiningTrafficPattern:
    """الگوی ترافیک ماینینگ"""
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str
    pattern_type: str
    confidence: float
    timestamp: datetime
    payload_preview: str
    packet_count: int
    total_bytes: int

class WiresharkMiningAnalyzer:
    """
    تحلیلگر ترافیک ماینینگ با استفاده از Wireshark
    """
    
    def __init__(self):
        self.mining_patterns = {
            # Bitcoin patterns
            'bitcoin': [
                r'bitcoin',
                r'blockchain',
                r'getblock',
                r'getheaders',
                r'inv',
                r'version',
                r'ping',
                r'pong'
            ],
            # Ethereum patterns
            'ethereum': [
                r'ethereum',
                r'eth_',
                r'web3',
                r'personal_',
                r'net_',
                r'eth_blockNumber',
                r'eth_getBalance'
            ],
            # Stratum mining protocol
            'stratum': [
                r'mining\.subscribe',
                r'mining\.authorize',
                r'mining\.submit',
                r'mining\.notify',
                r'mining\.set_difficulty',
                r'mining\.set_extranonce'
            ],
            # Pool mining patterns
            'pool_mining': [
                r'pool',
                r'worker',
                r'hashrate',
                r'shares',
                r'difficulty',
                r'nonce',
                r'target'
            ],
            # General crypto patterns
            'crypto_general': [
                r'cryptocurrency',
                r'mining',
                r'hash',
                r'block',
                r'wallet',
                r'address',
                r'private_key',
                r'public_key'
            ]
        }
        
        self.suspicious_ports = {
            8333, 8332, 18333, 18444,  # Bitcoin
            30303, 8545, 8546,         # Ethereum
            18080, 18081, 18082,       # Monero
            9333, 9332, 19333,         # Litecoin
            9999, 9998, 19999,         # Dash
            8233, 8232, 18233,         # Zcash
            3333, 3334, 3335, 3336,    # Stratum
            4028, 4029, 4030,          # Pool mining
            8080, 8888, 8889, 8890     # Web interfaces
        }
        
        self.vpn_proxy_indicators = [
            'vpn', 'proxy', 'tunnel', 'gateway', 'relay',
            'nordvpn', 'expressvpn', 'surfshark', 'cyberghost',
            'protonvpn', 'private internet access', 'tunnelbear'
        ]
    
    async def start_live_capture(self, interface: str = 'any', duration: int = 3600):
        """
        شروع ضبط زنده ترافیک
        """
        logger.info(f"🎯 Starting live capture on interface: {interface}")
        
        try:
            # ایجاد capture با PyShark
            capture = pyshark.LiveCapture(
                interface=interface,
                output_file=f'mining_traffic_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pcap'
            )
            
            # تنظیم فیلترهای ماینینگ
            mining_filters = [
                'tcp.port == 8333 or tcp.port == 30303 or tcp.port == 18080',
                'tcp.port == 3333 or tcp.port == 4028 or tcp.port == 8080',
                'tcp.port == 9333 or tcp.port == 9999 or tcp.port == 8233',
                'tcp contains "mining" or tcp contains "bitcoin"',
                'tcp contains "ethereum" or tcp contains "stratum"',
                'tcp contains "pool" or tcp contains "worker"'
            ]
            
            patterns = []
            start_time = time.time()
            
            for packet in capture.sniff_continuously():
                # بررسی محدودیت زمان
                if time.time() - start_time > duration:
                    break
                
                # تحلیل پکت
                pattern = await self._analyze_packet(packet)
                if pattern:
                    patterns.append(pattern)
                    logger.info(f"🎯 Mining pattern detected: {pattern.source_ip} -> {pattern.destination_ip}")
                
                # ذخیره هر 100 پکت
                if len(patterns) % 100 == 0:
                    await self._save_patterns(patterns[-100:])
            
            capture.close()
            return patterns
            
        except Exception as e:
            logger.error(f"Error in live capture: {e}")
            return []
    
    async def analyze_pcap_file(self, pcap_file: str) -> List[MiningTrafficPattern]:
        """
        تحلیل فایل PCAP
        """
        logger.info(f"📁 Analyzing PCAP file: {pcap_file}")
        
        try:
            capture = pyshark.FileCapture(pcap_file)
            patterns = []
            
            for packet in capture:
                pattern = await self._analyze_packet(packet)
                if pattern:
                    patterns.append(pattern)
            
            capture.close()
            
            logger.info(f"🎯 Found {len(patterns)} mining patterns in {pcap_file}")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing PCAP file: {e}")
            return []
    
    async def _analyze_packet(self, packet) -> Optional[MiningTrafficPattern]:
        """
        تحلیل پکت برای تشخیص الگوهای ماینینگ
        """
        try:
            # بررسی لایه‌های پکت
            if not hasattr(packet, 'ip') or not hasattr(packet, 'tcp'):
                return None
            
            source_ip = packet.ip.src
            dest_ip = packet.ip.dst
            source_port = int(packet.tcp.srcport)
            dest_port = int(packet.tcp.dstport)
            
            # بررسی پورت‌های مشکوک
            if source_port not in self.suspicious_ports and dest_port not in self.suspicious_ports:
                return None
            
            # استخراج payload
            payload = self._extract_payload(packet)
            if not payload:
                return None
            
            # تشخیص الگوی ماینینگ
            pattern_type, confidence = self._detect_mining_pattern(payload)
            if not pattern_type:
                return None
            
            # بررسی VPN/Proxy
            vpn_detected = self._detect_vpn_proxy(packet)
            
            pattern = MiningTrafficPattern(
                source_ip=source_ip,
                destination_ip=dest_ip,
                source_port=source_port,
                destination_port=dest_port,
                protocol='TCP',
                pattern_type=pattern_type,
                confidence=confidence,
                timestamp=datetime.now(),
                payload_preview=payload[:200],
                packet_count=1,
                total_bytes=len(payload)
            )
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analyzing packet: {e}")
            return None
    
    def _extract_payload(self, packet) -> Optional[str]:
        """
        استخراج payload از پکت
        """
        try:
            # تلاش برای استخراج payload از لایه‌های مختلف
            if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'payload'):
                return packet.tcp.payload
            
            if hasattr(packet, 'data'):
                return packet.data
            
            if hasattr(packet, 'payload'):
                return packet.payload
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting payload: {e}")
            return None
    
    def _detect_mining_pattern(self, payload: str) -> Tuple[Optional[str], float]:
        """
        تشخیص الگوی ماینینگ در payload
        """
        try:
            payload_lower = payload.lower()
            
            for pattern_type, patterns in self.mining_patterns.items():
                matches = 0
                for pattern in patterns:
                    if re.search(pattern, payload_lower, re.IGNORECASE):
                        matches += 1
                
                if matches > 0:
                    confidence = min(matches / len(patterns), 1.0)
                    return pattern_type, confidence
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Error detecting mining pattern: {e}")
            return None, 0.0
    
    def _detect_vpn_proxy(self, packet) -> bool:
        """
        تشخیص VPN/Proxy در پکت
        """
        try:
            # بررسی DNS queries
            if hasattr(packet, 'dns'):
                if hasattr(packet.dns, 'qry_name'):
                    qry_name = packet.dns.qry_name.lower()
                    for indicator in self.vpn_proxy_indicators:
                        if indicator in qry_name:
                            return True
            
            # بررسی HTTP headers
            if hasattr(packet, 'http'):
                if hasattr(packet.http, 'user_agent'):
                    user_agent = packet.http.user_agent.lower()
                    for indicator in self.vpn_proxy_indicators:
                        if indicator in user_agent:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting VPN/Proxy: {e}")
            return False
    
    async def _save_patterns(self, patterns: List[MiningTrafficPattern]):
        """
        ذخیره الگوهای تشخیص داده شده
        """
        try:
            async with aiofiles.open('mining_patterns.json', 'a') as f:
                for pattern in patterns:
                    pattern_data = {
                        'source_ip': pattern.source_ip,
                        'destination_ip': pattern.destination_ip,
                        'source_port': pattern.source_port,
                        'destination_port': pattern.destination_port,
                        'pattern_type': pattern.pattern_type,
                        'confidence': pattern.confidence,
                        'timestamp': pattern.timestamp.isoformat(),
                        'payload_preview': pattern.payload_preview,
                        'packet_count': pattern.packet_count,
                        'total_bytes': pattern.total_bytes
                    }
                    await f.write(json.dumps(pattern_data) + '\n')
                    
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")
    
    async def analyze_network_behavior(self, target_ip: str, duration: int = 300):
        """
        تحلیل رفتار شبکه برای IP خاص
        """
        logger.info(f"🔍 Analyzing network behavior for: {target_ip}")
        
        try:
            # فیلتر برای IP هدف
            capture_filter = f'host {target_ip}'
            
            capture = pyshark.LiveCapture(
                interface='any',
                display_filter=capture_filter
            )
            
            patterns = []
            start_time = time.time()
            
            for packet in capture.sniff_continuously():
                if time.time() - start_time > duration:
                    break
                
                pattern = await self._analyze_packet(packet)
                if pattern:
                    patterns.append(pattern)
            
            capture.close()
            
            # تحلیل آماری
            analysis = self._analyze_patterns_statistics(patterns)
            
            logger.info(f"📊 Network behavior analysis for {target_ip}: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing network behavior: {e}")
            return {}
    
    def _analyze_patterns_statistics(self, patterns: List[MiningTrafficPattern]) -> Dict[str, Any]:
        """
        تحلیل آماری الگوها
        """
        if not patterns:
            return {}
        
        try:
            # آمار کلی
            total_packets = len(patterns)
            total_bytes = sum(p.total_bytes for p in patterns)
            
            # توزیع الگوها
            pattern_distribution = {}
            for pattern in patterns:
                pattern_type = pattern.pattern_type
                pattern_distribution[pattern_type] = pattern_distribution.get(pattern_type, 0) + 1
            
            # IP های مقصد
            destination_ips = set(p.destination_ip for p in patterns)
            
            # پورت‌های مقصد
            destination_ports = set(p.destination_port for p in patterns)
            
            # میانگین اطمینان
            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            
            return {
                'total_packets': total_packets,
                'total_bytes': total_bytes,
                'pattern_distribution': pattern_distribution,
                'destination_ips': list(destination_ips),
                'destination_ports': list(destination_ports),
                'average_confidence': avg_confidence,
                'mining_likelihood': 'high' if avg_confidence > 0.7 else 'medium' if avg_confidence > 0.4 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns statistics: {e}")
            return {}
    
    async def start_monitoring_service(self, target_ranges: List[str] = None):
        """
        شروع سرویس نظارت مداوم
        """
        logger.info("🚀 Starting continuous mining traffic monitoring service...")
        
        while True:
            try:
                # اسکن ترافیک زنده
                patterns = await self.start_live_capture(duration=300)  # 5 دقیقه
                
                # تحلیل الگوها
                for pattern in patterns:
                    if pattern.confidence > 0.6:
                        logger.warning(f"⚠️ High-confidence mining activity detected: {pattern.source_ip}")
                        
                        # تحلیل رفتار شبکه
                        behavior = await self.analyze_network_behavior(pattern.source_ip, duration=60)
                        
                        # ذخیره گزارش
                        await self._save_mining_report(pattern, behavior)
                
                # انتظار قبل از اسکن بعدی
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in monitoring service: {e}")
                await asyncio.sleep(30)
    
    async def _save_mining_report(self, pattern: MiningTrafficPattern, behavior: Dict[str, Any]):
        """
        ذخیره گزارش ماینینگ
        """
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'pattern': {
                    'source_ip': pattern.source_ip,
                    'destination_ip': pattern.destination_ip,
                    'pattern_type': pattern.pattern_type,
                    'confidence': pattern.confidence,
                    'payload_preview': pattern.payload_preview
                },
                'behavior_analysis': behavior,
                'risk_level': 'high' if pattern.confidence > 0.8 else 'medium' if pattern.confidence > 0.6 else 'low'
            }
            
            async with aiofiles.open('mining_reports.json', 'a') as f:
                await f.write(json.dumps(report) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving mining report: {e}")

# Global analyzer instance
wireshark_analyzer = WiresharkMiningAnalyzer()

async def main():
    """
    تابع اصلی برای اجرای تحلیلگر
    """
    logger.info("🔍 Starting Wireshark Mining Traffic Analyzer...")
    
    # شروع سرویس نظارت مداوم
    await wireshark_analyzer.start_monitoring_service()

if __name__ == "__main__":
    asyncio.run(main()) 