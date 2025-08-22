#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoIP Lookup Module
Provides geolocation services for IP addresses with multiple provider support
"""

import logging
import requests
from typing import Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import json
import os

logger = logging.getLogger(__name__)

class GeoIPLookup:
    def __init__(self):
        # تنظیمات محدوده جغرافیایی استان ایلام
        self.ilam_bounds = {
            'north': 34.5,
            'south': 32.0, 
            'east': 48.5,
            'west': 45.5,
            'center': (33.63, 46.42)
        }
        
        # سرویس‌های مکان‌یابی IP
        self.providers = {
            'ip-api': {
                'url': 'http://ip-api.com/json/{ip}',
                'fields': ['lat', 'lon', 'city', 'regionName', 'country', 'isp'],
                'success_key': 'status',
                'success_value': 'success'
            },
            'ipapi': {
                'url': 'http://ipapi.co/{ip}/json/',
                'fields': ['latitude', 'longitude', 'city', 'region', 'country_name', 'org'],
                'error_key': 'error'
            }
        }
        
        # بارگذاری کش محلی برای کاهش درخواست‌ها
        self.cache_file = 'geoip_cache.json'
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """بارگذاری کش از فایل"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
        return {}

    def _save_cache(self):
        """ذخیره کش در فایل"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _query_provider(self, provider: str, ip: str) -> Optional[Dict[str, Any]]:
        """درخواست به یک سرویس مکان‌یابی"""
        config = self.providers[provider]
        try:
            response = requests.get(
                config['url'].format(ip=ip),
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                
                # بررسی خطا
                if config.get('error_key') and data.get(config['error_key']):
                    return None
                
                # بررسی موفقیت
                if config.get('success_key'):
                    if data.get(config['success_key']) != config['success_value']:
                        return None
                
                return self._normalize_response(provider, data)
                
        except Exception as e:
            logger.warning(f"Error querying {provider} for {ip}: {e}")
        return None

    def _normalize_response(self, provider: str, data: Dict) -> Dict[str, Any]:
        """استانداردسازی خروجی سرویس‌های مختلف"""
        if provider == 'ip-api':
            return {
                'lat': data.get('lat'),
                'lon': data.get('lon'),
                'city': data.get('city'),
                'region': data.get('regionName'),
                'country': data.get('country'),
                'isp': data.get('isp')
            }
        elif provider == 'ipapi':
            return {
                'lat': data.get('latitude'),
                'lon': data.get('longitude'),
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name'),
                'isp': data.get('org')
            }
        return data

    def _is_in_ilam(self, lat: float, lon: float) -> bool:
        """بررسی قرارگیری نقطه در محدوده استان ایلام"""
        if not (lat and lon):
            return False
        return (self.ilam_bounds['south'] <= lat <= self.ilam_bounds['north'] and
                self.ilam_bounds['west'] <= lon <= self.ilam_bounds['east'])

    def lookup(self, ip: str, use_cache: bool = True) -> Dict[str, Any]:
        """جستجوی موقعیت جغرافیایی IP"""
        # بررسی کش
        if use_cache and ip in self.cache:
            return self.cache[ip]
            
        results = {}
        
        # درخواست همزمان به همه سرویس‌ها
        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {
                provider: executor.submit(self._query_provider, provider, ip)
                for provider in self.providers
            }
            
            # جمع‌آوری نتایج
            for provider, future in futures.items():
                try:
                    result = future.result(timeout=10)
                    if result:
                        results[provider] = result
                        # اضافه کردن وضعیت قرارگیری در ایلام
                        if result.get('lat') and result.get('lon'):
                            results[provider]['in_ilam'] = self._is_in_ilam(
                                result['lat'], result['lon']
                            )
                except Exception as e:
                    logger.error(f"Error getting result from {provider}: {e}")
                    
        # ذخیره در کش
        if results:
            self.cache[ip] = results
            self._save_cache()
            
        return results

    def batch_lookup(self, ips: list) -> Dict[str, Dict]:
        """جستجوی همزمان چند IP"""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                ip: executor.submit(self.lookup, ip)
                for ip in ips
            }
            
            return {
                ip: future.result()
                for ip, future in futures.items()
            }

# مثال استفاده
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    geo = GeoIPLookup()
    test_ip = "8.8.8.8"  # Google DNS
    
    print(f"Looking up {test_ip}...")
    result = geo.lookup(test_ip)
    print(json.dumps(result, indent=2, ensure_ascii=False))
