#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Nmap Scanner for Cryptocurrency Mining Detection
اسکنر پیشرفته Nmap برای تشخیص ماینینگ رمزارز
"""

import asyncio
import subprocess
import nmap
import socket
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import aiofiles
import ipaddress

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NmapScanResult:
    """نتیجه اسکن Nmap"""
    ip_address: str
    hostname: Optional[str]
    open_ports: List[int]
    services: Dict[int, str]
    os_info: Optional[str]
    scan_time: datetime
    blockchain_ports: List[int]
    mining_indicators: List[str]
    vpn_proxy_detected: bool
    confidence_score: float
    details: Dict[str, Any]

class AdvancedNmapScanner:
    """
    اسکنر پیشرفته Nmap برای تشخیص ماینینگ رمزارز
    """
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        
        # پورت‌های بلاکچین و ماینینگ
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
            # Stratum Mining
            'stratum': [3333, 3334, 3335, 3336, 3337, 3338, 3339],
            # Pool Mining
            'pool_mining': [4028, 4029, 4030, 8080, 8888, 8889, 8890],
            # Web Interfaces
            'web_interfaces': [8080, 8081, 8082, 8888, 8889, 9000, 9001],
            # Other Crypto
            'other_crypto': [9333, 9334, 9335, 9336, 9337, 9338, 9339]
        }
        
        # نشانه‌های ماینینگ
        self.mining_indicators = [
            'bitcoin', 'ethereum', 'mining', 'pool', 'stratum',
            'blockchain', 'crypto', 'hash', 'worker', 'shares',
            'difficulty', 'nonce', 'target', 'wallet', 'address'
        ]
        
        # نشانه‌های VPN/Proxy
        self.vpn_proxy_indicators = [
            'vpn', 'proxy', 'tunnel', 'gateway', 'relay',
            'nordvpn', 'expressvpn', 'surfshark', 'cyberghost',
            'protonvpn', 'private internet access', 'tunnelbear',
            'windscribe', 'mullvad', 'ivpn', 'perfect privacy'
        ]
    
    async def scan_global_network(self, target_ranges: List[str] = None) -> List[NmapScanResult]:
        """
        اسکن شبکه جهانی برای یافتن ماینرها
        """
        if not target_ranges:
            # محدوده‌های جهانی مهم
            target_ranges = [
                "0.0.0.0/0",  # تمام IP ها (با محدودیت)
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16",
                "100.64.0.0/10",
                "169.254.0.0/16"
            ]
        
        all_results = []
        
        for target_range in target_ranges:
            logger.info(f"🔍 Scanning global network: {target_range}")
            
            try:
                results = await self._scan_network_range(target_range)
                all_results.extend(results)
                
            except Exception as e:
                logger.error(f"Error scanning {target_range}: {e}")
        
        return all_results
    
    async def _scan_network_range(self, target_range: str) -> List[NmapScanResult]:
        """
        اسکن محدوده شبکه
        """
        results = []
        
        try:
            # اسکن سریع با Nmap
            scan_args = [
                '-sS',  # SYN scan
                '-sU',  # UDP scan
                '--top-ports', '1000',
                '--script', 'banner,http-title,http-headers,ssl-cert',
                '--script-args', 'banner.maxlen=1000',
                '--max-retries', '2',
                '--host-timeout', '30s',
                '--max-rate', '1000'  # محدودیت نرخ
            ]
            
            # اضافه کردن پورت‌های بلاکچین
            blockchain_ports = []
            for ports in self.blockchain_ports.values():
                blockchain_ports.extend(ports)
            
            scan_args.extend(['-p', ','.join(map(str, blockchain_ports))])
            
            logger.info(f"Starting Nmap scan: {target_range}")
            result = self.nm.scan(hosts=target_range, arguments=' '.join(scan_args))
            
            for host in result['scan']:
                if result['scan'][host]['status']['state'] == 'up':
                    scan_result = await self._analyze_host(host, result['scan'][host])
                    if scan_result:
                        results.append(scan_result)
            
        except Exception as e:
            logger.error(f"Error in network range scan: {e}")
        
        return results
    
    async def _analyze_host(self, host: str, host_info: Dict) -> Optional[NmapScanResult]:
        """
        تحلیل میزبان
        """
        try:
            open_ports = []
            services = {}
            blockchain_ports_found = []
            mining_indicators_found = []
            
            # تحلیل پورت‌های TCP
            if 'tcp' in host_info:
                for port, port_info in host_info['tcp'].items():
                    if port_info['state'] == 'open':
                        open_ports.append(port)
                        services[port] = port_info.get('name', 'unknown')
                        
                        # بررسی پورت‌های بلاکچین
                        if port in self._get_all_blockchain_ports():
                            blockchain_ports_found.append(port)
                        
                        # بررسی نشانه‌های ماینینگ در banner
                        banner = port_info.get('script', {}).get('banner', '')
                        if banner:
                            indicators = self._detect_mining_indicators(banner)
                            mining_indicators_found.extend(indicators)
            
            # تحلیل پورت‌های UDP
            if 'udp' in host_info:
                for port, port_info in host_info['udp'].items():
                    if port_info['state'] == 'open':
                        open_ports.append(port)
                        services[port] = port_info.get('name', 'unknown')
                        
                        if port in self._get_all_blockchain_ports():
                            blockchain_ports_found.append(port)
            
            # اگر هیچ پورت بلاکچین پیدا نشد، رد کن
            if not blockchain_ports_found:
                return None
            
            # تشخیص VPN/Proxy
            vpn_proxy_detected = await self._detect_vpn_proxy(host)
            
            # محاسبه امتیاز اطمینان
            confidence_score = self._calculate_confidence_score(
                blockchain_ports_found, mining_indicators_found, vpn_proxy_detected
            )
            
            # دریافت اطلاعات OS
            os_info = None
            if 'osmatch' in host_info and host_info['osmatch']:
                os_info = host_info['osmatch'][0]['name']
            
            # دریافت hostname
            hostname = host_info.get('hostnames', [{}])[0].get('name')
            
            scan_result = NmapScanResult(
                ip_address=host,
                hostname=hostname,
                open_ports=open_ports,
                services=services,
                os_info=os_info,
                scan_time=datetime.now(),
                blockchain_ports=blockchain_ports_found,
                mining_indicators=mining_indicators_found,
                vpn_proxy_detected=vpn_proxy_detected,
                confidence_score=confidence_score,
                details={
                    'host_info': host_info,
                    'scan_duration': host_info.get('scan_duration', 0)
                }
            )
            
            logger.info(f"🎯 Mining host detected: {host} (confidence: {confidence_score:.2f})")
            return scan_result
            
        except Exception as e:
            logger.error(f"Error analyzing host {host}: {e}")
            return None
    
    def _get_all_blockchain_ports(self) -> List[int]:
        """
        دریافت تمام پورت‌های بلاکچین
        """
        all_ports = []
        for ports in self.blockchain_ports.values():
            all_ports.extend(ports)
        return all_ports
    
    def _detect_mining_indicators(self, text: str) -> List[str]:
        """
        تشخیص نشانه‌های ماینینگ در متن
        """
        indicators = []
        text_lower = text.lower()
        
        for indicator in self.mining_indicators:
            if indicator in text_lower:
                indicators.append(indicator)
        
        return indicators
    
    async def _detect_vpn_proxy(self, host: str) -> bool:
        """
        تشخیص VPN/Proxy
        """
        try:
            # بررسی DNS
            try:
                hostname = socket.gethostbyaddr(host)[0]
                hostname_lower = hostname.lower()
                
                for indicator in self.vpn_proxy_indicators:
                    if indicator in hostname_lower:
                        return True
            except:
                pass
            
            # بررسی WHOIS
            whois_info = await self._get_whois_info(host)
            if whois_info:
                for indicator in self.vpn_proxy_indicators:
                    if indicator in whois_info.lower():
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting VPN/Proxy for {host}: {e}")
            return False
    
    async def _get_whois_info(self, host: str) -> Optional[str]:
        """
        دریافت اطلاعات WHOIS
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://ip-api.com/json/{host}') as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"{data.get('isp', '')} {data.get('org', '')}"
            return None
            
        except Exception as e:
            logger.error(f"Error getting WHOIS info: {e}")
            return None
    
    def _calculate_confidence_score(self, blockchain_ports: List[int], 
                                  mining_indicators: List[str], 
                                  vpn_proxy_detected: bool) -> float:
        """
        محاسبه امتیاز اطمینان
        """
        score = 0.0
        
        # امتیاز بر اساس پورت‌های بلاکچین
        score += len(blockchain_ports) * 0.2
        
        # امتیاز بر اساس نشانه‌های ماینینگ
        score += len(mining_indicators) * 0.15
        
        # امتیاز اضافی برای VPN/Proxy (احتمال ماینینگ بیشتر)
        if vpn_proxy_detected:
            score += 0.3
        
        # محدود کردن امتیاز به 1.0
        return min(score, 1.0)
    
    async def scan_specific_targets(self, targets: List[str]) -> List[NmapScanResult]:
        """
        اسکن اهداف خاص
        """
        results = []
        
        for target in targets:
            logger.info(f"🎯 Scanning specific target: {target}")
            
            try:
                # اسکن عمیق برای هدف خاص
                scan_args = [
                    '-sS', '-sU', '-sV',  # Version detection
                    '--script', 'banner,http-title,http-headers,ssl-cert,http-enum',
                    '--script-args', 'banner.maxlen=2000',
                    '--max-retries', '3',
                    '--host-timeout', '60s'
                ]
                
                # اضافه کردن تمام پورت‌های بلاکچین
                blockchain_ports = self._get_all_blockchain_ports()
                scan_args.extend(['-p', ','.join(map(str, blockchain_ports))])
                
                result = self.nm.scan(hosts=target, arguments=' '.join(scan_args))
                
                if target in result['scan'] and result['scan'][target]['status']['state'] == 'up':
                    scan_result = await self._analyze_host(target, result['scan'][target])
                    if scan_result:
                        results.append(scan_result)
                
            except Exception as e:
                logger.error(f"Error scanning target {target}: {e}")
        
        return results
    
    async def continuous_monitoring(self, target_ranges: List[str] = None, interval: int = 3600):
        """
        نظارت مداوم
        """
        logger.info("🚀 Starting continuous Nmap monitoring...")
        
        while True:
            try:
                logger.info("🔍 Starting monitoring cycle...")
                
                # اسکن شبکه
                results = await self.scan_global_network(target_ranges)
                
                # فیلتر نتایج با اطمینان بالا
                high_confidence_results = [r for r in results if r.confidence_score > 0.7]
                
                # ذخیره نتایج
                await self._save_scan_results(high_confidence_results)
                
                # گزارش
                logger.info(f"📊 Monitoring cycle completed: {len(results)} total, {len(high_confidence_results)} high-confidence")
                
                # انتظار تا اسکن بعدی
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(300)  # 5 دقیقه انتظار در صورت خطا
    
    async def _save_scan_results(self, results: List[NmapScanResult]):
        """
        ذخیره نتایج اسکن
        """
        try:
            async with aiofiles.open('nmap_scan_results.json', 'a') as f:
                for result in results:
                    result_data = {
                        'ip_address': result.ip_address,
                        'hostname': result.hostname,
                        'blockchain_ports': result.blockchain_ports,
                        'mining_indicators': result.mining_indicators,
                        'vpn_proxy_detected': result.vpn_proxy_detected,
                        'confidence_score': result.confidence_score,
                        'scan_time': result.scan_time.isoformat(),
                        'services': result.services,
                        'os_info': result.os_info
                    }
                    await f.write(json.dumps(result_data) + '\n')
                    
        except Exception as e:
            logger.error(f"Error saving scan results: {e}")
    
    async def generate_mining_report(self, results: List[NmapScanResult]) -> Dict[str, Any]:
        """
        تولید گزارش ماینینگ
        """
        try:
            if not results:
                return {}
            
            # آمار کلی
            total_hosts = len(results)
            high_confidence_hosts = len([r for r in results if r.confidence_score > 0.8])
            medium_confidence_hosts = len([r for r in results if 0.5 <= r.confidence_score <= 0.8])
            
            # توزیع پورت‌های بلاکچین
            port_distribution = {}
            for result in results:
                for port in result.blockchain_ports:
                    port_distribution[port] = port_distribution.get(port, 0) + 1
            
            # توزیع نشانه‌های ماینینگ
            indicator_distribution = {}
            for result in results:
                for indicator in result.mining_indicators:
                    indicator_distribution[indicator] = indicator_distribution.get(indicator, 0) + 1
            
            # آمار VPN/Proxy
            vpn_proxy_count = len([r for r in results if r.vpn_proxy_detected])
            
            # IP های با بالاترین اطمینان
            top_hosts = sorted(results, key=lambda x: x.confidence_score, reverse=True)[:10]
            
            report = {
                'scan_timestamp': datetime.now().isoformat(),
                'total_hosts_scanned': total_hosts,
                'high_confidence_hosts': high_confidence_hosts,
                'medium_confidence_hosts': medium_confidence_hosts,
                'vpn_proxy_hosts': vpn_proxy_count,
                'port_distribution': port_distribution,
                'indicator_distribution': indicator_distribution,
                'top_hosts': [
                    {
                        'ip': r.ip_address,
                        'confidence': r.confidence_score,
                        'blockchain_ports': r.blockchain_ports,
                        'mining_indicators': r.mining_indicators,
                        'vpn_proxy': r.vpn_proxy_detected
                    }
                    for r in top_hosts
                ],
                'risk_assessment': {
                    'high_risk': high_confidence_hosts,
                    'medium_risk': medium_confidence_hosts,
                    'low_risk': total_hosts - high_confidence_hosts - medium_confidence_hosts
                }
            }
            
            # ذخیره گزارش
            async with aiofiles.open('mining_report.json', 'w') as f:
                await f.write(json.dumps(report, indent=2))
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating mining report: {e}")
            return {}

# Global scanner instance
nmap_scanner = AdvancedNmapScanner()

async def main():
    """
    تابع اصلی برای اجرای اسکنر
    """
    logger.info("🔍 Starting Advanced Nmap Scanner...")
    
    # اسکن اولیه
    results = await nmap_scanner.scan_global_network()
    
    # تولید گزارش
    report = await nmap_scanner.generate_mining_report(results)
    
    logger.info(f"📊 Scan completed: {len(results)} hosts found")
    logger.info(f"📋 Report generated: {report.get('high_confidence_hosts', 0)} high-confidence hosts")
    
    # شروع نظارت مداوم
    await nmap_scanner.continuous_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 