#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Geolocation System for National Miner Detection
سیستم پیشرفته مکان‌یابی برای کشف ماینرهای غیرمجاز
"""

import asyncio
import aiohttp
import json
import logging
import sqlite3
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import requests
from geopy.geocoders import Nominatim, GoogleV3
from geopy.distance import geodesic
import folium
from folium import plugins
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import reverse_geocoder as rg
import phonenumbers
from phonenumbers import geocoder, carrier
import opencage
from opencage.geocoder import OpenCageGeocode
import ipapi
import geoip2.database
import geoip2.errors
from shapely.geometry import Point, Polygon
import geopandas as gpd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LocationData:
    """Data class for location information"""
    latitude: float
    longitude: float
    accuracy: float
    city: str
    region: str
    country: str
    postal_code: str
    address: str
    isp: str
    timezone: str
    source: str
    confidence: float
    timestamp: datetime

@dataclass
class OwnerInfo:
    """Data class for owner information"""
    name: str
    phone: str
    national_id: str
    address: str
    postal_code: str
    city: str
    region: str
    country: str
    email: Optional[str] = None
    company: Optional[str] = None
    registration_date: Optional[datetime] = None
    verification_status: str = "pending"

class AdvancedGeolocationSystem:
    """
    سیستم پیشرفته مکان‌یابی با قابلیت‌های کامل
    """
    
    def __init__(self):
        self.geolocators = {}
        self.api_keys = {}
        self.cache_db = "geolocation_cache.db"
        self.ilam_bounds = {
            'north': 34.5,
            'south': 32.0,
            'east': 48.5,
            'west': 45.5
        }
        
        # Initialize geolocators
        self._initialize_geolocators()
        
        # Initialize cache database
        self._initialize_cache()
        
        # Load Ilam province data
        self.ilam_data = self._load_ilam_data()
    
    def _initialize_geolocators(self):
        """Initialize multiple geolocation services"""
        try:
            # Nominatim (OpenStreetMap)
            self.geolocators['nominatim'] = Nominatim(
                user_agent="NationalMinerDetectionSystem/1.0"
            )
            
            # Google Geocoding (if API key available)
            google_api_key = self._get_api_key('GOOGLE_MAPS_API_KEY')
            if google_api_key:
                self.geolocators['google'] = GoogleV3(api_key=google_api_key)
            
            # OpenCage Geocoding
            opencage_api_key = self._get_api_key('OPENCAGE_API_KEY')
            if opencage_api_key:
                self.geolocators['opencage'] = OpenCageGeocode(opencage_api_key)
            
            # IP-API (free tier)
            self.geolocators['ipapi'] = None  # Direct HTTP requests
            
            logger.info("Geolocators initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing geolocators: {e}")
    
    def _get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from environment or config"""
        import os
        return os.getenv(key_name)
    
    def _initialize_cache(self):
        """Initialize geolocation cache database"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geolocation_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE,
                    latitude REAL,
                    longitude REAL,
                    city TEXT,
                    region TEXT,
                    country TEXT,
                    isp TEXT,
                    accuracy REAL,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS owner_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE,
                    mac_address TEXT,
                    owner_name TEXT,
                    phone TEXT,
                    national_id TEXT,
                    address TEXT,
                    verification_status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Cache database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing cache: {e}")
    
    def _load_ilam_data(self) -> Dict:
        """Load Ilam province geographical data"""
        ilam_data = {
            'cities': {
                'ایلام': {'lat': 33.6374, 'lon': 46.4227, 'population': 194030},
                'مهران': {'lat': 33.1221, 'lon': 46.1641, 'population': 18556},
                'دهلران': {'lat': 32.6942, 'lon': 47.2678, 'population': 32580},
                'آبدانان': {'lat': 32.9928, 'lon': 47.4164, 'population': 23430},
                'دره‌شهر': {'lat': 33.1458, 'lon': 47.3667, 'population': 15650},
                'ایوان': {'lat': 33.8081, 'lon': 46.2892, 'population': 12520},
                'چرداول': {'lat': 33.7333, 'lon': 46.8833, 'population': 8900},
                'بدره': {'lat': 33.0833, 'lon': 47.1167, 'population': 7600},
                'سرابله': {'lat': 32.9667, 'lon': 46.5833, 'population': 6800},
                'ملکشاهی': {'lat': 33.3833, 'lon': 46.5667, 'population': 5200}
            },
            'districts': {},
            'neighborhoods': {}
        }
        
        return ilam_data
    
    async def geolocate_ip_advanced(self, ip_address: str) -> LocationData:
        """
        Advanced IP geolocation using multiple services
        """
        # Check cache first
        cached_data = self._get_cached_location(ip_address)
        if cached_data and self._is_cache_valid(cached_data):
            return cached_data
        
        # Try multiple geolocation services
        location_results = []
        
        # 1. IP-API (free, reliable)
        try:
            ipapi_result = await self._geolocate_ipapi(ip_address)
            if ipapi_result:
                location_results.append(ipapi_result)
        except Exception as e:
            logger.warning(f"IP-API failed for {ip_address}: {e}")
        
        # 2. GeoIP2 database
        try:
            geoip2_result = await self._geolocate_geoip2(ip_address)
            if geoip2_result:
                location_results.append(geoip2_result)
        except Exception as e:
            logger.warning(f"GeoIP2 failed for {ip_address}: {e}")
        
        # 3. OpenCage (if available)
        if 'opencage' in self.geolocators:
            try:
                opencage_result = await self._geolocate_opencage(ip_address)
                if opencage_result:
                    location_results.append(opencage_result)
            except Exception as e:
                logger.warning(f"OpenCage failed for {ip_address}: {e}")
        
        # Combine results and calculate consensus
        if location_results:
            final_location = self._combine_location_results(location_results, ip_address)
            self._cache_location(final_location)
            return final_location
        else:
            raise Exception(f"All geolocation services failed for {ip_address}")
    
    async def _geolocate_ipapi(self, ip_address: str) -> Optional[LocationData]:
        """Geolocate using IP-API service"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'success':
                            return LocationData(
                                latitude=float(data.get('lat', 0)),
                                longitude=float(data.get('lon', 0)),
                                accuracy=0.8,  # IP-API accuracy
                                city=data.get('city', ''),
                                region=data.get('regionName', ''),
                                country=data.get('country', ''),
                                postal_code=data.get('zip', ''),
                                address=f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}",
                                isp=data.get('isp', ''),
                                timezone=data.get('timezone', ''),
                                source='ip-api',
                                confidence=0.85,
                                timestamp=datetime.now()
                            )
        except Exception as e:
            logger.error(f"IP-API error: {e}")
        
        return None
    
    async def _geolocate_geoip2(self, ip_address: str) -> Optional[LocationData]:
        """Geolocate using GeoIP2 database"""
        try:
            # This would require GeoIP2 database file
            # For now, return None
            return None
        except Exception as e:
            logger.error(f"GeoIP2 error: {e}")
        
        return None
    
    async def _geolocate_opencage(self, ip_address: str) -> Optional[LocationData]:
        """Geolocate using OpenCage service"""
        try:
            if 'opencage' in self.geolocators:
                result = self.geolocators['opencage'].geocode(ip_address)
                if result:
                    return LocationData(
                        latitude=result['geometry']['lat'],
                        longitude=result['geometry']['lng'],
                        accuracy=0.9,
                        city=result['components'].get('city', ''),
                        region=result['components'].get('state', ''),
                        country=result['components'].get('country', ''),
                        postal_code=result['components'].get('postcode', ''),
                        address=result['formatted'],
                        isp='',
                        timezone='',
                        source='opencage',
                        confidence=0.9,
                        timestamp=datetime.now()
                    )
        except Exception as e:
            logger.error(f"OpenCage error: {e}")
        
        return None
    
    def _combine_location_results(self, results: List[LocationData], ip_address: str) -> LocationData:
        """Combine multiple geolocation results for better accuracy"""
        if len(results) == 1:
            return results[0]
        
        # Calculate weighted average based on confidence
        total_weight = sum(r.confidence for r in results)
        weighted_lat = sum(r.latitude * r.confidence for r in results) / total_weight
        weighted_lon = sum(r.longitude * r.confidence for r in results) / total_weight
        
        # Use most common city/region
        cities = [r.city for r in results if r.city]
        regions = [r.region for r in results if r.region]
        countries = [r.country for r in results if r.country]
        
        from collections import Counter
        most_common_city = Counter(cities).most_common(1)[0][0] if cities else ''
        most_common_region = Counter(regions).most_common(1)[0][0] if regions else ''
        most_common_country = Counter(countries).most_common(1)[0][0] if countries else ''
        
        # Calculate combined confidence
        combined_confidence = min(0.95, sum(r.confidence for r in results) / len(results) + 0.1)
        
        return LocationData(
            latitude=weighted_lat,
            longitude=weighted_lon,
            accuracy=min(r.accuracy for r in results),
            city=most_common_city,
            region=most_common_region,
            country=most_common_country,
            postal_code=results[0].postal_code,
            address=f"{most_common_city}, {most_common_region}, {most_common_country}",
            isp=results[0].isp,
            timezone=results[0].timezone,
            source='combined',
            confidence=combined_confidence,
            timestamp=datetime.now()
        )
    
    def _get_cached_location(self, ip_address: str) -> Optional[LocationData]:
        """Get cached location data"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT latitude, longitude, accuracy, city, region, country, 
                       postal_code, address, isp, timezone, source, confidence, timestamp
                FROM geolocation_cache 
                WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return LocationData(
                    latitude=row[0],
                    longitude=row[1],
                    accuracy=row[2],
                    city=row[3],
                    region=row[4],
                    country=row[5],
                    postal_code=row[6],
                    address=row[7],
                    isp=row[8],
                    timezone=row[9],
                    source=row[10],
                    confidence=row[11],
                    timestamp=datetime.fromisoformat(row[12])
                )
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    def _is_cache_valid(self, location_data: LocationData) -> bool:
        """Check if cached data is still valid (less than 24 hours old)"""
        return (datetime.now() - location_data.timestamp).total_seconds() < 86400
    
    def _cache_location(self, location_data: LocationData):
        """Cache location data"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO geolocation_cache 
                (ip_address, latitude, longitude, accuracy, city, region, country,
                 postal_code, address, isp, timezone, source, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                location_data.latitude, location_data.longitude, location_data.accuracy,
                location_data.city, location_data.region, location_data.country,
                location_data.postal_code, location_data.address, location_data.isp,
                location_data.timezone, location_data.source, location_data.confidence,
                location_data.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    async def identify_owner_advanced(self, ip_address: str, mac_address: Optional[str] = None) -> OwnerInfo:
        """
        Advanced owner identification using multiple sources
        """
        # Check cache first
        cached_owner = self._get_cached_owner(ip_address)
        if cached_owner:
            return cached_owner
        
        owner_info = OwnerInfo(
            name="",
            phone="",
            national_id="",
            address="",
            postal_code="",
            city="",
            region="",
            country="",
            verification_status="pending"
        )
        
        # 1. Get location first
        try:
            location = await self.geolocate_ip_advanced(ip_address)
            owner_info.city = location.city
            owner_info.region = location.region
            owner_info.country = location.country
            owner_info.address = location.address
        except Exception as e:
            logger.warning(f"Location lookup failed: {e}")
        
        # 2. Try to get owner info from ISP
        if location.isp:
            isp_owner = await self._get_owner_from_isp(ip_address, location.isp)
            if isp_owner:
                owner_info.name = isp_owner.get('name', '')
                owner_info.phone = isp_owner.get('phone', '')
        
        # 3. Try reverse phone lookup if available
        if owner_info.phone:
            phone_info = await self._reverse_phone_lookup(owner_info.phone)
            if phone_info:
                owner_info.name = phone_info.get('name', owner_info.name)
                owner_info.address = phone_info.get('address', owner_info.address)
        
        # 4. Try national ID lookup if available
        if owner_info.national_id:
            national_info = await self._lookup_national_id(owner_info.national_id)
            if national_info:
                owner_info.name = national_info.get('name', owner_info.name)
                owner_info.address = national_info.get('address', owner_info.address)
        
        # Cache the result
        self._cache_owner(ip_address, mac_address, owner_info)
        
        return owner_info
    
    async def _get_owner_from_isp(self, ip_address: str, isp: str) -> Optional[Dict]:
        """Get owner information from ISP"""
        # This would require ISP cooperation or database access
        # For now, return None
        return None
    
    async def _reverse_phone_lookup(self, phone: str) -> Optional[Dict]:
        """Reverse phone number lookup"""
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone, "IR")
            
            # Get carrier info
            carrier_name = carrier.name_for_number(parsed_number, "fa")
            
            # Get location info
            location_info = geocoder.description_for_number(parsed_number, "fa")
            
            return {
                'carrier': carrier_name,
                'location': location_info
            }
        except Exception as e:
            logger.error(f"Phone lookup error: {e}")
        
        return None
    
    async def _lookup_national_id(self, national_id: str) -> Optional[Dict]:
        """Lookup national ID (requires government database access)"""
        # This would require access to government databases
        # For now, return None
        return None
    
    def _get_cached_owner(self, ip_address: str) -> Optional[OwnerInfo]:
        """Get cached owner information"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT owner_name, phone, national_id, address, verification_status, timestamp
                FROM owner_cache 
                WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return OwnerInfo(
                    name=row[0] or "",
                    phone=row[1] or "",
                    national_id=row[2] or "",
                    address=row[3] or "",
                    postal_code="",
                    city="",
                    region="",
                    country="",
                    verification_status=row[4] or "pending"
                )
        except Exception as e:
            logger.error(f"Owner cache retrieval error: {e}")
        
        return None
    
    def _cache_owner(self, ip_address: str, mac_address: Optional[str], owner_info: OwnerInfo):
        """Cache owner information"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO owner_cache 
                (ip_address, mac_address, owner_name, phone, national_id, address, verification_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                ip_address, mac_address, owner_info.name, owner_info.phone,
                owner_info.national_id, owner_info.address, owner_info.verification_status
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Owner cache storage error: {e}")
    
    def is_in_ilam_province(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are within Ilam province"""
        return (self.ilam_bounds['south'] <= latitude <= self.ilam_bounds['north'] and
                self.ilam_bounds['west'] <= longitude <= self.ilam_bounds['east'])
    
    def get_nearest_city(self, latitude: float, longitude: float) -> Dict:
        """Get nearest city in Ilam province"""
        nearest_city = None
        min_distance = float('inf')
        
        for city_name, city_data in self.ilam_data['cities'].items():
            distance = geodesic(
                (latitude, longitude),
                (city_data['lat'], city_data['lon'])
            ).kilometers
            
            if distance < min_distance:
                min_distance = distance
                nearest_city = {
                    'name': city_name,
                    'distance_km': distance,
                    'coordinates': (city_data['lat'], city_data['lon']),
                    'population': city_data['population']
                }
        
        return nearest_city or {}
    
    def create_heatmap(self, detections: List[Dict]) -> str:
        """Create heatmap of detections"""
        try:
            # Create base map centered on Ilam
            m = folium.Map(
                location=[33.6374, 46.4227],
                zoom_start=8,
                tiles='OpenStreetMap'
            )
            
            # Add heatmap layer
            heat_data = []
            for detection in detections:
                if detection.get('latitude') and detection.get('longitude'):
                    heat_data.append([
                        detection['latitude'],
                        detection['longitude'],
                        detection.get('confidence_score', 1)
                    ])
            
            if heat_data:
                plugins.HeatMap(heat_data).add_to(m)
            
            # Add markers for individual detections
            for detection in detections:
                if detection.get('latitude') and detection.get('longitude'):
                    folium.Marker(
                        [detection['latitude'], detection['longitude']],
                        popup=f"IP: {detection.get('ip_address', 'N/A')}<br>"
                              f"Confidence: {detection.get('confidence_score', 0)}%<br>"
                              f"Threat: {detection.get('threat_level', 'unknown')}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
            
            # Save map
            map_file = f"detection_heatmap_{int(time.time())}.html"
            m.save(map_file)
            
            return map_file
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {e}")
            return ""
    
    def analyze_detection_clusters(self, detections: List[Dict]) -> Dict:
        """Analyze detection clusters for patterns"""
        try:
            # Extract coordinates
            coordinates = []
            for detection in detections:
                if detection.get('latitude') and detection.get('longitude'):
                    coordinates.append([detection['latitude'], detection['longitude']])
            
            if len(coordinates) < 2:
                return {'clusters': [], 'total_clusters': 0}
            
            # Normalize coordinates
            scaler = StandardScaler()
            coordinates_scaled = scaler.fit_transform(coordinates)
            
            # Apply DBSCAN clustering
            clustering = DBSCAN(eps=0.1, min_samples=2).fit(coordinates_scaled)
            
            # Analyze clusters
            cluster_labels = clustering.labels_
            unique_labels = set(cluster_labels)
            
            clusters = []
            for label in unique_labels:
                if label == -1:  # Noise points
                    continue
                
                cluster_points = [i for i, l in enumerate(cluster_labels) if l == label]
                cluster_detections = [detections[i] for i in cluster_points]
                
                # Calculate cluster statistics
                cluster_coords = [coordinates[i] for i in cluster_points]
                center_lat = np.mean([c[0] for c in cluster_coords])
                center_lon = np.mean([c[1] for c in cluster_coords])
                
                clusters.append({
                    'cluster_id': label,
                    'center': {'latitude': center_lat, 'longitude': center_lon},
                    'detection_count': len(cluster_detections),
                    'average_confidence': np.mean([d.get('confidence_score', 0) for d in cluster_detections]),
                    'threat_levels': [d.get('threat_level', 'unknown') for d in cluster_detections],
                    'detections': cluster_detections
                })
            
            return {
                'clusters': clusters,
                'total_clusters': len(clusters),
                'total_detections': len(detections),
                'clustered_detections': len([l for l in cluster_labels if l != -1])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing clusters: {e}")
            return {'clusters': [], 'total_clusters': 0, 'error': str(e)}

# Global instance
geolocation_system = AdvancedGeolocationSystem() 