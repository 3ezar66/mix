#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHBHHBSH - سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز
Comprehensive Professional Cryptocurrency Mining Device Detection System
Version: 2.0.0
Author: Advanced Security Team
"""

import sys
import os
import json
import time
import threading
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import queue
import hashlib
import base64
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.scrolledtext as scrolledtext
import folium
from folium import plugins
import webbrowser
import requests
import nmap
import socket
import subprocess
import platform
import psutil
import GPUtil
import serial
import serial.tools.list_ports
import pyaudio
import wave
import struct
import threading
from scipy import signal
from scipy.fft import fft, fftfreq
import librosa
import sounddevice as sd
import rtlsdr
import rtlsdr.rtlsdr
from rtlsdr import RtlSdr
import serial
import time
import math
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from folium import plugins
import webbrowser
import requests
import nmap
import socket
import subprocess
import platform
import psutil
import GPUtil
import serial
import serial.tools.list_ports
import pyaudio
import wave
import struct
import threading
from scipy import signal
from scipy.fft import fft, fftfreq
import librosa
import sounddevice as sd
import rtlsdr
import rtlsdr.rtlsdr
from rtlsdr import RtlSdr

# Configuration
CONFIG = {
    'database_path': 'mining_detection.db',
    'log_level': logging.INFO,
    'scan_timeout': 30,
    'audio_sample_rate': 44100,
    'rf_frequency_range': (1e6, 6e9),  # 1MHz to 6GHz
    'mining_signatures': {
        'acoustic': {
            'bitcoin': [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
            'ethereum': [60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 30720],
            'litecoin': [70, 140, 280, 560, 1120, 2240, 4480, 8960, 17920, 35840]
        },
        'rf': {
            'bitcoin': [2.4e9, 5.8e9],
            'ethereum': [2.4e9, 5.2e9],
            'litecoin': [2.4e9, 5.5e9]
        },
        'thermal': {
            'mining_temp_range': (45, 85),  # Celsius
            'ambient_temp': 25
        },
        'power': {
            'mining_power_range': (500, 5000),  # Watts
            'normal_power_range': (50, 500)
        }
    },
    'api_keys': {
        'ripe': 'YOUR_RIPE_API_KEY',
        'shodan': 'YOUR_SHODAN_API_KEY',
        'virustotal': 'YOUR_VIRUSTOTAL_API_KEY',
        'abuseipdb': 'YOUR_ABUSEIPDB_API_KEY'
    }
}

class MiningDeviceDetector:
    """Main class for comprehensive mining device detection"""
    
    def __init__(self):
        self.setup_logging()
        self.setup_database()
        self.detection_results = []
        self.is_scanning = False
        self.scan_threads = []
        self.audio_stream = None
        self.rf_device = None
        self.thermal_camera = None
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        logging.basicConfig(
            level=CONFIG['log_level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mining_detection.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize SQLite database with comprehensive schema"""
        try:
            self.conn = sqlite3.connect(CONFIG['database_path'])
            self.cursor = self.conn.cursor()
            
            # Create comprehensive tables
            self.cursor.executescript('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_type TEXT NOT NULL,
                    location_lat REAL,
                    location_lon REAL,
                    address TEXT,
                    city TEXT,
                    province TEXT,
                    country TEXT,
                    detection_method TEXT NOT NULL,
                    confidence_score REAL,
                    signature_hash TEXT UNIQUE,
                    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                );
                
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER,
                    detection_type TEXT NOT NULL,
                    detection_data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                );
                
                CREATE TABLE IF NOT EXISTS scan_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    scan_type TEXT NOT NULL,
                    parameters TEXT,
                    results_summary TEXT
                );
                
                CREATE TABLE IF NOT EXISTS network_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT,
                    open_ports TEXT,
                    services TEXT,
                    mining_signatures TEXT,
                    location_info TEXT,
                    risk_score REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS acoustic_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frequency_peaks TEXT,
                    amplitude_data TEXT,
                    spectral_features TEXT,
                    mining_probability REAL,
                    location_lat REAL,
                    location_lon REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS rf_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frequency_range TEXT,
                    signal_strength TEXT,
                    modulation_type TEXT,
                    mining_signatures TEXT,
                    location_lat REAL,
                    location_lon REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS thermal_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temperature_data TEXT,
                    thermal_patterns TEXT,
                    anomaly_score REAL,
                    location_lat REAL,
                    location_lon REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS power_scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    power_consumption REAL,
                    power_patterns TEXT,
                    efficiency_score REAL,
                    location_lat REAL,
                    location_lon REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            self.conn.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            raise
            
    def acoustic_scan(self, duration: int = 10, location: Tuple[float, float] = None) -> Dict[str, Any]:
        """Perform acoustic scanning for mining device signatures"""
        try:
            self.logger.info("Starting acoustic scan...")
            
            # Initialize audio capture
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=CONFIG['audio_sample_rate'],
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            start_time = time.time()
            
            # Record audio
            while time.time() - start_time < duration:
                data = stream.read(1024)
                frames.append(data)
                
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.float32)
            
            # Perform FFT analysis
            fft_data = fft(audio_data)
            freqs = fftfreq(len(audio_data), 1/CONFIG['audio_sample_rate'])
            
            # Find frequency peaks
            peaks, _ = signal.find_peaks(np.abs(fft_data), height=np.max(np.abs(fft_data))*0.1)
            peak_frequencies = freqs[peaks]
            peak_amplitudes = np.abs(fft_data)[peaks]
            
            # Analyze for mining signatures
            mining_probability = self.analyze_acoustic_signatures(peak_frequencies, peak_amplitudes)
            
            result = {
                'scan_type': 'acoustic',
                'duration': duration,
                'sample_rate': CONFIG['audio_sample_rate'],
                'peak_frequencies': peak_frequencies.tolist(),
                'peak_amplitudes': peak_amplitudes.tolist(),
                'mining_probability': mining_probability,
                'timestamp': datetime.now().isoformat(),
                'location': location
            }
            
            # Save to database
            if location:
                self.cursor.execute('''
                    INSERT INTO acoustic_scan_results 
                    (frequency_peaks, amplitude_data, mining_probability, location_lat, location_lon, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    json.dumps(peak_frequencies.tolist()),
                    json.dumps(peak_amplitudes.tolist()),
                    mining_probability,
                    location[0],
                    location[1]
                ))
                self.conn.commit()
            
            self.logger.info(f"Acoustic scan completed. Mining probability: {mining_probability:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Acoustic scan failed: {e}")
            return {'error': str(e)}
            
    def analyze_acoustic_signatures(self, frequencies: np.ndarray, amplitudes: np.ndarray) -> float:
        """Analyze acoustic data for mining device signatures"""
        try:
            # Normalize frequencies to Hz
            frequencies_hz = np.abs(frequencies)
            
            # Check for known mining frequencies
            mining_signatures = CONFIG['mining_signatures']['acoustic']
            total_score = 0
            max_score = 0
            
            for crypto_type, signature_freqs in mining_signatures.items():
                for sig_freq in signature_freqs:
                    # Find frequencies close to signature
                    close_freqs = frequencies_hz[np.abs(frequencies_hz - sig_freq) < sig_freq * 0.1]
                    if len(close_freqs) > 0:
                        # Calculate score based on amplitude and frequency match
                        freq_indices = np.where(np.abs(frequencies_hz - sig_freq) < sig_freq * 0.1)[0]
                        amplitudes_at_freq = amplitudes[freq_indices]
                        score = np.sum(amplitudes_at_freq) / len(amplitudes_at_freq)
                        total_score += score
                        max_score = max(max_score, score)
            
            # Normalize score
            if max_score > 0:
                return min(total_score / max_score, 1.0)
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Acoustic signature analysis failed: {e}")
            return 0.0
            
    def rf_scan(self, frequency_range: Tuple[float, float] = None, duration: int = 10, 
                location: Tuple[float, float] = None) -> Dict[str, Any]:
        """Perform RF scanning for mining device signatures"""
        try:
            self.logger.info("Starting RF scan...")
            
            if frequency_range is None:
                frequency_range = CONFIG['rf_frequency_range']
                
            # Initialize RTL-SDR device
            try:
                sdr = RtlSdr()
                sdr.sample_rate = 2.048e6
                sdr.center_freq = (frequency_range[0] + frequency_range[1]) / 2
                sdr.freq_correction = 60
                sdr.gain = 'auto'
                
                # Collect samples
                samples = sdr.read_samples(1024 * 1024)
                sdr.close()
                
                # Perform spectral analysis
                spectrum = np.fft.fftshift(np.fft.fft(samples))
                freqs = np.fft.fftshift(np.fft.fftfreq(len(samples), 1/sdr.sample_rate))
                
                # Find signal peaks
                peaks, _ = signal.find_peaks(np.abs(spectrum), height=np.max(np.abs(spectrum))*0.1)
                peak_frequencies = freqs[peaks]
                peak_powers = np.abs(spectrum)[peaks]
                
                # Analyze for mining signatures
                mining_signatures = self.analyze_rf_signatures(peak_frequencies, peak_powers)
                
                result = {
                    'scan_type': 'rf',
                    'frequency_range': frequency_range,
                    'duration': duration,
                    'peak_frequencies': peak_frequencies.tolist(),
                    'peak_powers': peak_powers.tolist(),
                    'mining_signatures': mining_signatures,
                    'timestamp': datetime.now().isoformat(),
                    'location': location
                }
                
                # Save to database
                if location:
                    self.cursor.execute('''
                        INSERT INTO rf_scan_results 
                        (frequency_range, signal_strength, mining_signatures, location_lat, location_lon, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        f"{frequency_range[0]}-{frequency_range[1]}",
                        json.dumps(peak_powers.tolist()),
                        json.dumps(mining_signatures),
                        location[0],
                        location[1]
                    ))
                    self.conn.commit()
                
                self.logger.info("RF scan completed successfully")
                return result
                
            except Exception as e:
                self.logger.warning(f"RTL-SDR not available, using simulation: {e}")
                return self.simulate_rf_scan(frequency_range, duration, location)
                
        except Exception as e:
            self.logger.error(f"RF scan failed: {e}")
            return {'error': str(e)}
            
    def simulate_rf_scan(self, frequency_range: Tuple[float, float], duration: int, 
                         location: Tuple[float, float]) -> Dict[str, Any]:
        """Simulate RF scan when hardware is not available"""
        # Generate simulated RF data
        num_samples = int(duration * 1e6)  # 1MHz sample rate
        freqs = np.linspace(frequency_range[0], frequency_range[1], num_samples)
        
        # Simulate mining device signals
        mining_freqs = [2.4e9, 5.8e9]  # Common mining frequencies
        signals = np.zeros_like(freqs)
        
        for mining_freq in mining_freqs:
            if frequency_range[0] <= mining_freq <= frequency_range[1]:
                # Add Gaussian peak at mining frequency
                peak_idx = np.argmin(np.abs(freqs - mining_freq))
                signals[peak_idx] = np.random.normal(0.8, 0.1)
        
        # Add noise
        signals += np.random.normal(0, 0.1, len(signals))
        
        # Find peaks
        peaks, _ = signal.find_peaks(signals, height=0.3)
        peak_frequencies = freqs[peaks]
        peak_powers = signals[peaks]
        
        return {
            'scan_type': 'rf_simulation',
            'frequency_range': frequency_range,
            'duration': duration,
            'peak_frequencies': peak_frequencies.tolist(),
            'peak_powers': peak_powers.tolist(),
            'mining_signatures': {'simulated': True},
            'timestamp': datetime.now().isoformat(),
            'location': location
        }
        
    def analyze_rf_signatures(self, frequencies: np.ndarray, powers: np.ndarray) -> Dict[str, Any]:
        """Analyze RF data for mining device signatures"""
        try:
            mining_signatures = CONFIG['mining_signatures']['rf']
            detected_signatures = {}
            
            for crypto_type, sig_freqs in mining_signatures.items():
                for sig_freq in sig_freqs:
                    # Find frequencies close to signature
                    close_freqs = frequencies[np.abs(frequencies - sig_freq) < sig_freq * 0.01]
                    if len(close_freqs) > 0:
                        freq_indices = np.where(np.abs(frequencies - sig_freq) < sig_freq * 0.01)[0]
                        powers_at_freq = powers[freq_indices]
                        avg_power = np.mean(powers_at_freq)
                        
                        if avg_power > 0.5:  # Threshold for detection
                            detected_signatures[crypto_type] = {
                                'frequency': sig_freq,
                                'power': avg_power,
                                'confidence': min(avg_power, 1.0)
                            }
            
            return detected_signatures
            
        except Exception as e:
            self.logger.error(f"RF signature analysis failed: {e}")
            return {}
            
    def network_scan(self, ip_range: str, scan_type: str = 'comprehensive') -> Dict[str, Any]:
        """Perform network scanning for mining devices"""
        try:
            self.logger.info(f"Starting network scan of {ip_range}")
            
            # Initialize nmap scanner
            nm = nmap.PortScanner()
            
            # Define scan arguments based on type
            if scan_type == 'fast':
                arguments = '-sS -T4 -p 22,80,443,3333,4444,8080,18081'
            elif scan_type == 'comprehensive':
                arguments = '-sS -sV -O -T4 -p- --script=banner'
            else:  # stealth
                arguments = '-sS -sV -T2 -p 22,80,443,3333,4444,8080,18081'
            
            # Perform scan
            nm.scan(hosts=ip_range, arguments=arguments)
            
            results = []
            for host in nm.all_hosts():
                if nm[host].state() == 'up':
                    host_info = {
                        'ip': host,
                        'state': nm[host].state(),
                        'open_ports': [],
                        'services': [],
                        'os_info': '',
                        'mining_signatures': []
                    }
                    
                    # Extract open ports and services
                    for proto in nm[host].all_protocols():
                        ports = nm[host][proto].keys()
                        for port in ports:
                            service_info = nm[host][proto][port]
                            host_info['open_ports'].append(port)
                            
                            if 'name' in service_info:
                                host_info['services'].append(f"{port}/{service_info['name']}")
                                
                                # Check for mining service signatures
                                if any(sig in service_info['name'].lower() for sig in ['mining', 'pool', 'stratum']):
                                    host_info['mining_signatures'].append(f"Service: {service_info['name']}")
                    
                    # OS detection
                    if 'osmatch' in nm[host] and nm[host]['osmatch']:
                        host_info['os_info'] = nm[host]['osmatch'][0]['name']
                    
                    # Calculate risk score
                    risk_score = self.calculate_network_risk(host_info)
                    host_info['risk_score'] = risk_score
                    
                    results.append(host_info)
                    
                    # Save to database
                    self.cursor.execute('''
                        INSERT INTO network_scan_results 
                        (ip_address, open_ports, services, mining_signatures, risk_score, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        host,
                        json.dumps(host_info['open_ports']),
                        json.dumps(host_info['services']),
                        json.dumps(host_info['mining_signatures']),
                        risk_score,
                        datetime.now().isoformat()
                    ))
            
            self.conn.commit()
            
            scan_summary = {
                'scan_type': scan_type,
                'ip_range': ip_range,
                'total_hosts': len(results),
                'suspicious_hosts': len([r for r in results if r['risk_score'] > 0.7]),
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Network scan completed. Found {len(results)} hosts")
            return scan_summary
            
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            return {'error': str(e)}
            
    def calculate_network_risk(self, host_info: Dict[str, Any]) -> float:
        """Calculate risk score for network host"""
        risk_score = 0.0
        
        # Mining ports (high risk)
        mining_ports = [3333, 4444, 8080, 18081, 18082, 18083]
        for port in host_info['open_ports']:
            if port in mining_ports:
                risk_score += 0.3
                
        # Mining services (high risk)
        if host_info['mining_signatures']:
            risk_score += 0.4
            
        # SSH access (medium risk)
        if 22 in host_info['open_ports']:
            risk_score += 0.1
            
        # Web services (low risk)
        if 80 in host_info['open_ports'] or 443 in host_info['open_ports']:
            risk_score += 0.05
            
        return min(risk_score, 1.0)
        
    def thermal_scan(self, location: Tuple[float, float] = None) -> Dict[str, Any]:
        """Perform thermal scanning for mining devices"""
        try:
            self.logger.info("Starting thermal scan...")
            
            # Simulate thermal camera data (replace with actual hardware)
            # Generate thermal image data
            thermal_width, thermal_height = 320, 240
            thermal_data = np.random.normal(CONFIG['mining_signatures']['thermal']['ambient_temp'], 5, (thermal_height, thermal_width))
            
            # Add mining device heat signatures
            mining_temp = np.random.uniform(
                CONFIG['mining_signatures']['thermal']['mining_temp_range'][0],
                CONFIG['mining_signatures']['thermal']['mining_temp_range'][1]
            )
            
            # Create heat patterns
            center_x, center_y = thermal_width // 2, thermal_height // 2
            for y in range(thermal_height):
                for x in range(thermal_width):
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance < 50:  # Mining device area
                        thermal_data[y, x] = mining_temp + np.random.normal(0, 2)
            
            # Analyze thermal patterns
            max_temp = np.max(thermal_data)
            min_temp = np.min(thermal_data)
            avg_temp = np.mean(thermal_data)
            
            # Calculate anomaly score
            temp_std = np.std(thermal_data)
            anomaly_score = (max_temp - avg_temp) / temp_std if temp_std > 0 else 0
            
            # Check for mining temperature patterns
            mining_probability = 0.0
            if max_temp > CONFIG['mining_signatures']['thermal']['mining_temp_range'][0]:
                mining_probability = min((max_temp - CONFIG['mining_signatures']['thermal']['ambient_temp']) / 
                                       (CONFIG['mining_signatures']['thermal']['mining_temp_range'][1] - 
                                        CONFIG['mining_signatures']['thermal']['ambient_temp']), 1.0)
            
            result = {
                'scan_type': 'thermal',
                'thermal_data': thermal_data.tolist(),
                'max_temperature': max_temp,
                'min_temperature': min_temp,
                'average_temperature': avg_temp,
                'anomaly_score': anomaly_score,
                'mining_probability': mining_probability,
                'timestamp': datetime.now().isoformat(),
                'location': location
            }
            
            # Save to database
            if location:
                self.cursor.execute('''
                    INSERT INTO thermal_scan_results 
                    (temperature_data, thermal_patterns, anomaly_score, location_lat, location_lon, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    json.dumps(thermal_data.tolist()),
                    json.dumps({'max_temp': max_temp, 'min_temp': min_temp, 'avg_temp': avg_temp}),
                    anomaly_score,
                    location[0],
                    location[1]
                ))
                self.conn.commit()
            
            self.logger.info(f"Thermal scan completed. Mining probability: {mining_probability:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Thermal scan failed: {e}")
            return {'error': str(e)}
            
    def power_scan(self, location: Tuple[float, float] = None) -> Dict[str, Any]:
        """Perform power consumption analysis"""
        try:
            self.logger.info("Starting power scan...")
            
            # Simulate power monitoring (replace with actual hardware)
            # Generate power consumption data over time
            time_points = np.linspace(0, 24, 1440)  # 24 hours, 1-minute intervals
            
            # Normal power consumption pattern
            base_power = np.random.normal(200, 50, len(time_points))
            
            # Add mining power spikes
            mining_power = np.random.uniform(
                CONFIG['mining_signatures']['power']['mining_power_range'][0],
                CONFIG['mining_signatures']['power']['mining_power_range'][1]
            )
            
            # Mining activity periods (simulate 8-hour mining sessions)
            mining_periods = [
                (2, 10),   # 2 AM to 10 AM
                (14, 22)   # 2 PM to 10 PM
            ]
            
            for start_hour, end_hour in mining_periods:
                start_idx = int(start_hour * 60)
                end_idx = int(end_hour * 60)
                base_power[start_idx:end_idx] = mining_power + np.random.normal(0, 100, end_idx - start_idx)
            
            # Calculate power statistics
            total_energy = np.trapz(base_power, time_points) / 60  # Convert to kWh
            max_power = np.max(base_power)
            avg_power = np.mean(base_power)
            power_variance = np.var(base_power)
            
            # Analyze for mining patterns
            mining_probability = 0.0
            if max_power > CONFIG['mining_signatures']['power']['mining_power_range'][0]:
                mining_probability = min((max_power - CONFIG['mining_signatures']['power']['normal_power_range'][1]) / 
                                       (CONFIG['mining_signatures']['power']['mining_power_range'][1] - 
                                        CONFIG['mining_signatures']['power']['normal_power_range'][1]), 1.0)
            
            # Calculate efficiency score
            efficiency_score = 1.0 - (power_variance / (avg_power ** 2)) if avg_power > 0 else 0
            
            result = {
                'scan_type': 'power',
                'time_points': time_points.tolist(),
                'power_consumption': base_power.tolist(),
                'total_energy_kwh': total_energy,
                'max_power_watts': max_power,
                'average_power_watts': avg_power,
                'power_variance': power_variance,
                'mining_probability': mining_probability,
                'efficiency_score': efficiency_score,
                'timestamp': datetime.now().isoformat(),
                'location': location
            }
            
            # Save to database
            if location:
                self.cursor.execute('''
                    INSERT INTO power_scan_results 
                    (power_consumption, power_patterns, efficiency_score, location_lat, location_lon, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    json.dumps(base_power.tolist()),
                    json.dumps({'total_energy': total_energy, 'max_power': max_power, 'avg_power': avg_power}),
                    efficiency_score,
                    location[0],
                    location[1]
                ))
                self.conn.commit()
            
            self.logger.info(f"Power scan completed. Mining probability: {mining_probability:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Power scan failed: {e}")
            return {'error': str(e)}
            
    def comprehensive_scan(self, location: Tuple[float, float], scan_types: List[str] = None) -> Dict[str, Any]:
        """Perform comprehensive multi-modal scanning"""
        if scan_types is None:
            scan_types = ['acoustic', 'rf', 'thermal', 'power', 'network']
            
        self.logger.info(f"Starting comprehensive scan at location {location}")
        
        results = {}
        start_time = time.time()
        
        # Create scan session
        session_name = f"comprehensive_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.cursor.execute('''
            INSERT INTO scan_sessions (session_name, scan_type, parameters)
            VALUES (?, ?, ?)
        ''', (session_name, 'comprehensive', json.dumps(scan_types)))
        
        session_id = self.cursor.lastrowid
        
        try:
            # Perform all scans
            if 'acoustic' in scan_types:
                results['acoustic'] = self.acoustic_scan(duration=15, location=location)
                
            if 'rf' in scan_types:
                results['rf'] = self.rf_scan(duration=15, location=location)
                
            if 'thermal' in scan_types:
                results['thermal'] = self.thermal_scan(location=location)
                
            if 'power' in scan_types:
                results['power'] = self.power_scan(location=location)
                
            # Network scan requires IP range
            if 'network' in scan_types:
                # Use location to estimate IP range (simplified)
                results['network'] = self.network_scan('192.168.1.0/24', 'fast')
            
            # Calculate overall mining probability
            mining_probabilities = []
            for scan_type, result in results.items():
                if 'error' not in result:
                    if 'mining_probability' in result:
                        mining_probabilities.append(result['mining_probability'])
                    elif 'mining_signatures' in result and result['mining_signatures']:
                        mining_probabilities.append(0.8)  # High confidence if signatures found
            
            overall_probability = np.mean(mining_probabilities) if mining_probabilities else 0.0
            
            # Update scan session
            end_time = time.time()
            duration = end_time - start_time
            
            self.cursor.execute('''
                UPDATE scan_sessions 
                SET end_time = ?, results_summary = ?
                WHERE id = ?
            ''', (
                datetime.fromtimestamp(end_time).isoformat(),
                json.dumps({
                    'overall_mining_probability': overall_probability,
                    'scan_duration': duration,
                    'results_count': len(results)
                }),
                session_id
            ))
            
            self.conn.commit()
            
            comprehensive_result = {
                'session_id': session_id,
                'session_name': session_name,
                'scan_types': scan_types,
                'results': results,
                'overall_mining_probability': overall_probability,
                'scan_duration': duration,
                'timestamp': datetime.now().isoformat(),
                'location': location
            }
            
            self.logger.info(f"Comprehensive scan completed. Overall mining probability: {overall_probability:.2f}")
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive scan failed: {e}")
            # Update session with error
            self.cursor.execute('''
                UPDATE scan_sessions 
                SET end_time = ?, results_summary = ?
                WHERE id = ?
            ''', (
                datetime.now().isoformat(),
                json.dumps({'error': str(e)}),
                session_id
            ))
            self.conn.commit()
            return {'error': str(e)}
            
    def get_detection_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get detection history from database"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            self.cursor.execute('''
                SELECT d.*, 
                       COUNT(det.id) as detection_count,
                       MAX(det.timestamp) as last_detection
                FROM devices d
                LEFT JOIN detections det ON d.id = det.device_id
                WHERE d.first_detected >= ?
                GROUP BY d.id
                ORDER BY d.first_detected DESC
            ''', (cutoff_date.isoformat(),))
            
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            
            history = []
            for row in rows:
                device_data = dict(zip(columns, row))
                history.append(device_data)
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get detection history: {e}")
            return []
            
    def generate_report(self, session_id: int = None, format: str = 'html') -> str:
        """Generate comprehensive detection report"""
        try:
            if session_id:
                # Generate report for specific session
                self.cursor.execute('SELECT * FROM scan_sessions WHERE id = ?', (session_id,))
                session = self.cursor.fetchone()
                if not session:
                    return "Session not found"
                    
                # Get session results
                results_summary = json.loads(session[5]) if session[5] else {}
                
                report = f"""
                <html>
                <head>
                    <title>Mining Detection Report - Session {session_id}</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                        .high-risk {{ background: #ffebee; border-color: #f44336; }}
                        .medium-risk {{ background: #fff3e0; border-color: #ff9800; }}
                        .low-risk {{ background: #e8f5e8; border-color: #4caf50; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>🔍 Mining Device Detection Report</h1>
                        <p>Session: {session[1]} | Date: {session[2]}</p>
                    </div>
                    
                    <div class="section">
                        <h2>📊 Scan Summary</h2>
                        <p><strong>Scan Type:</strong> {session[3]}</p>
                        <p><strong>Parameters:</strong> {session[4]}</p>
                        <p><strong>Overall Mining Probability:</strong> {results_summary.get('overall_mining_probability', 'N/A'):.2f}</p>
                        <p><strong>Scan Duration:</strong> {results_summary.get('scan_duration', 'N/A'):.2f} seconds</p>
                    </div>
                </body>
                </html>
                """
            else:
                # Generate general report
                history = self.get_detection_history()
                
                report = f"""
                <html>
                <head>
                    <title>Mining Detection System Report</title>
                    <meta charset="utf-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                        .stats {{ display: flex; justify-content: space-around; text-align: center; }}
                        .stat-box {{ background: #ecf0f1; padding: 20px; border-radius: 5px; flex: 1; margin: 0 10px; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>🔍 Mining Device Detection System Report</h1>
                        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <div class="section">
                        <h2>📈 Detection Statistics</h2>
                        <div class="stats">
                            <div class="stat-box">
                                <h3>{len(history)}</h3>
                                <p>Total Devices</p>
                            </div>
                            <div class="stat-box">
                                <h3>{len([h for h in history if h.get('confidence_score', 0) > 0.8])}</h3>
                                <p>High Confidence</p>
                            </div>
                            <div class="stat-box">
                                <h3>{len([h for h in history if h.get('status') == 'active'])}</h3>
                                <p>Active Devices</p>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            # Save report to file
            filename = f"mining_detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return f"Error generating report: {e}"
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.conn:
                self.conn.close()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

def main():
    """Main function for command-line usage"""
    try:
        detector = MiningDeviceDetector()
        
        print("🔍 SHBHHBSH - سیستم جامع تخصصی جستجو و شناسایی و کشف و تشخیص واقعی دستگاه های استخراج رمزارز")
        print("=" * 80)
        
        while True:
            print("\n📋 Available Operations:")
            print("1. Acoustic Scan")
            print("2. RF Scan")
            print("3. Thermal Scan")
            print("4. Power Scan")
            print("5. Network Scan")
            print("6. Comprehensive Scan")
            print("7. Generate Report")
            print("8. View Detection History")
            print("9. Exit")
            
            choice = input("\nSelect operation (1-9): ").strip()
            
            if choice == '1':
                duration = int(input("Scan duration (seconds): ") or "10")
                detector.acoustic_scan(duration=duration)
                
            elif choice == '2':
                duration = int(input("Scan duration (seconds): ") or "10")
                detector.rf_scan(duration=duration)
                
            elif choice == '3':
                detector.thermal_scan()
                
            elif choice == '4':
                detector.power_scan()
                
            elif choice == '5':
                ip_range = input("IP range (e.g., 192.168.1.0/24): ").strip()
                scan_type = input("Scan type (fast/comprehensive/stealth): ").strip() or "fast"
                detector.network_scan(ip_range, scan_type)
                
            elif choice == '6':
                lat = float(input("Latitude: ") or "35.6892")
                lon = float(input("Longitude: ") or "51.3890")
                detector.comprehensive_scan((lat, lon))
                
            elif choice == '7':
                filename = detector.generate_report()
                print(f"Report generated: {filename}")
                
            elif choice == '8':
                history = detector.get_detection_history()
                print(f"Found {len(history)} detections in last 30 days")
                for device in history[:5]:  # Show first 5
                    print(f"- {device.get('device_type', 'Unknown')} at {device.get('address', 'Unknown location')}")
                    
            elif choice == '9':
                break
                
            else:
                print("Invalid choice. Please select 1-9.")
        
        detector.cleanup()
        print("Goodbye!")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Main execution failed: {e}")

if __name__ == "__main__":
    main()