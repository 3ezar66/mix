#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHBHHBSH Advanced - ماژول پیشرفته تشخیص ماینر
Advanced Mining Detection Module with AI and Machine Learning
"""

import numpy as np
import cv2
import librosa
import sounddevice as sd
from scipy import signal
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
import threading
import queue

class AdvancedMiningDetector:
    """کلاس پیشرفته تشخیص ماینر با الگوریتم‌های هوشمند"""
    
    def __init__(self):
        self.mining_patterns = self.load_mining_patterns()
        self.detection_threshold = 0.75
        self.confidence_scores = {}
        
    def load_mining_patterns(self) -> Dict[str, Any]:
        """بارگذاری الگوهای شناخته شده ماینر"""
        return {
            'bitcoin': {
                'acoustic': {
                    'frequencies': [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600],
                    'patterns': ['hash_algorithm', 'cooling_fan', 'power_supply'],
                    'confidence': 0.95
                },
                'rf': {
                    'frequencies': [2.4e9, 5.8e9],
                    'modulation': ['QPSK', 'QAM16', 'QAM64'],
                    'confidence': 0.90
                },
                'thermal': {
                    'temp_range': (45, 85),
                    'patterns': ['gpu_cluster', 'asic_array'],
                    'confidence': 0.88
                },
                'power': {
                    'consumption_range': (500, 5000),
                    'patterns': ['constant_load', 'hash_rate_variation'],
                    'confidence': 0.92
                }
            },
            'ethereum': {
                'acoustic': {
                    'frequencies': [60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 30720],
                    'patterns': ['memory_intensive', 'gpu_optimized'],
                    'confidence': 0.93
                },
                'rf': {
                    'frequencies': [2.4e9, 5.2e9],
                    'modulation': ['OFDM', 'MIMO'],
                    'confidence': 0.87
                },
                'thermal': {
                    'temp_range': (50, 90),
                    'patterns': ['gpu_memory', 'compute_units'],
                    'confidence': 0.85
                },
                'power': {
                    'consumption_range': (300, 4000),
                    'patterns': ['memory_bus_activity', 'compute_cycles'],
                    'confidence': 0.89
                }
            },
            'litecoin': {
                'acoustic': {
                    'frequencies': [70, 140, 280, 560, 1120, 2240, 4480, 8960, 17920, 35840],
                    'patterns': ['scrypt_algorithm', 'memory_hard'],
                    'confidence': 0.91
                },
                'rf': {
                    'frequencies': [2.4e9, 5.5e9],
                    'modulation': ['BPSK', 'QPSK'],
                    'confidence': 0.84
                },
                'thermal': {
                    'temp_range': (40, 80),
                    'patterns': ['memory_intensive', 'cpu_heavy'],
                    'confidence': 0.83
                },
                'power': {
                    'consumption_range': (400, 4500),
                    'patterns': ['memory_bus', 'cpu_cycles'],
                    'confidence': 0.86
                }
            }
        }
    
    def advanced_acoustic_analysis(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """تحلیل پیشرفته صوتی با الگوریتم‌های هوشمند"""
        try:
            # تبدیل به فرکانس
            fft_data = fft(audio_data)
            freqs = fftfreq(len(audio_data), 1/sample_rate)
            
            # یافتن قله‌های فرکانسی
            peaks, properties = signal.find_peaks(
                np.abs(fft_data), 
                height=np.max(np.abs(fft_data))*0.1,
                prominence=np.max(np.abs(fft_data))*0.05
            )
            
            peak_frequencies = freqs[peaks]
            peak_amplitudes = np.abs(fft_data)[peaks]
            
            # تحلیل الگوهای ماینر
            mining_detection = self.analyze_mining_acoustic_patterns(peak_frequencies, peak_amplitudes)
            
            # تحلیل ویژگی‌های طیفی
            spectral_features = self.extract_spectral_features(audio_data, sample_rate)
            
            # محاسبه امتیاز اطمینان
            confidence_score = self.calculate_acoustic_confidence(mining_detection, spectral_features)
            
            return {
                'detection_type': 'advanced_acoustic',
                'mining_detection': mining_detection,
                'spectral_features': spectral_features,
                'confidence_score': confidence_score,
                'peak_frequencies': peak_frequencies.tolist(),
                'peak_amplitudes': peak_amplitudes.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f"تحلیل صوتی پیشرفته ناموفق: {str(e)}"}
    
    def analyze_mining_acoustic_patterns(self, frequencies: np.ndarray, amplitudes: np.ndarray) -> Dict[str, Any]:
        """تحلیل الگوهای صوتی ماینر"""
        results = {}
        
        for crypto_type, patterns in self.mining_patterns.items():
            crypto_score = 0
            detected_patterns = []
            
            # بررسی فرکانس‌های شناخته شده
            for known_freq in patterns['acoustic']['frequencies']:
                # یافتن فرکانس‌های نزدیک
                close_freqs = frequencies[np.abs(frequencies - known_freq) < known_freq * 0.1]
                if len(close_freqs) > 0:
                    freq_indices = np.where(np.abs(frequencies - known_freq) < known_freq * 0.1)[0]
                    amplitudes_at_freq = amplitudes[freq_indices]
                    
                    # محاسبه امتیاز بر اساس دامنه
                    pattern_score = np.mean(amplitudes_at_freq) / np.max(amplitudes)
                    crypto_score += pattern_score
                    detected_patterns.append(f"freq_{known_freq}")
            
            # بررسی الگوهای شناخته شده
            for pattern in patterns['acoustic']['patterns']:
                if self.detect_pattern_in_audio(pattern, frequencies, amplitudes):
                    crypto_score += 0.2
                    detected_patterns.append(pattern)
            
            if crypto_score > 0:
                results[crypto_type] = {
                    'score': crypto_score,
                    'patterns': detected_patterns,
                    'confidence': min(crypto_score, 1.0)
                }
        
        return results
    
    def detect_pattern_in_audio(self, pattern: str, frequencies: np.ndarray, amplitudes: np.ndarray) -> bool:
        """تشخیص الگوی خاص در سیگنال صوتی"""
        try:
            if pattern == 'hash_algorithm':
                # الگوی الگوریتم هش - فرکانس‌های منظم
                freq_spacing = np.diff(frequencies)
                regular_spacing = np.std(freq_spacing) < np.mean(freq_spacing) * 0.1
                return regular_spacing
                
            elif pattern == 'cooling_fan':
                # الگوی فن خنک‌کننده - فرکانس‌های پایین با نوسان
                low_freqs = frequencies[frequencies < 1000]
                if len(low_freqs) > 0:
                    low_freq_amplitudes = amplitudes[frequencies < 1000]
                    variation = np.std(low_freq_amplitudes) / np.mean(low_freq_amplitudes)
                    return variation > 0.3
                
            elif pattern == 'power_supply':
                # الگوی منبع تغذیه - هارمونیک‌های 50/60Hz
                power_freqs = [50, 60, 100, 120, 150, 180]
                for power_freq in power_freqs:
                    if any(np.abs(frequencies - power_freq) < power_freq * 0.05):
                        return True
                        
            elif pattern == 'memory_intensive':
                # الگوی حافظه - فرکانس‌های بالا با پهنای باند زیاد
                high_freqs = frequencies[frequencies > 10000]
                if len(high_freqs) > 0:
                    high_freq_amplitudes = amplitudes[frequencies > 10000]
                    bandwidth = np.sum(high_freq_amplitudes)
                    return bandwidth > np.mean(amplitudes) * 2
                    
            elif pattern == 'gpu_optimized':
                # الگوی GPU - فرکانس‌های متوسط با الگوی منظم
                mid_freqs = frequencies[(frequencies >= 1000) & (frequencies <= 10000)]
                if len(mid_freqs) > 5:
                    mid_freq_amplitudes = amplitudes[(frequencies >= 1000) & (frequencies <= 10000)]
                    regularity = np.std(mid_freq_amplitudes) / np.mean(mid_freq_amplitudes)
                    return regularity < 0.5
                    
            elif pattern == 'scrypt_algorithm':
                # الگوی Scrypt - فرکانس‌های پیچیده
                complexity = len(frequencies) / len(amplitudes)
                return complexity > 0.8
                
            elif pattern == 'memory_hard':
                # الگوی حافظه سخت - فرکانس‌های بالا با تغییرات سریع
                high_freqs = frequencies[frequencies > 15000]
                if len(high_freqs) > 0:
                    freq_changes = np.diff(high_freqs)
                    rapid_changes = np.sum(freq_changes > np.mean(freq_changes) * 2)
                    return rapid_changes > len(high_freqs) * 0.3
                    
            elif pattern == 'cpu_heavy':
                # الگوی CPU - فرکانس‌های پایین با ثبات
                low_freqs = frequencies[frequencies < 500]
                if len(low_freqs) > 0:
                    low_freq_amplitudes = amplitudes[frequencies < 500]
                    stability = np.std(low_freq_amplitudes) / np.mean(low_freq_amplitudes)
                    return stability < 0.2
                    
        except Exception as e:
            print(f"خطا در تشخیص الگو {pattern}: {e}")
            
        return False
    
    def extract_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """استخراج ویژگی‌های طیفی پیشرفته"""
        try:
            # ویژگی‌های MFCC
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # ویژگی‌های طیفی
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            # ویژگی‌های ریتم
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # ویژگی‌های انرژی
            rms = librosa.feature.rms(y=audio_data)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            return {
                'mfcc_mean': mfcc_mean.tolist(),
                'mfcc_std': mfcc_std.tolist(),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_rolloff_std': float(np.std(spectral_rolloff)),
                'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
                'spectral_bandwidth_std': float(np.std(spectral_bandwidth)),
                'tempo': float(tempo),
                'rms_mean': float(np.mean(rms)),
                'rms_std': float(np.std(rms)),
                'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
                'zero_crossing_rate_std': float(np.std(zero_crossing_rate))
            }
            
        except Exception as e:
            return {'error': f"استخراج ویژگی‌های طیفی ناموفق: {str(e)}"}
    
    def calculate_acoustic_confidence(self, mining_detection: Dict[str, Any], spectral_features: Dict[str, Any]) -> float:
        """محاسبه امتیاز اطمینان تحلیل صوتی"""
        try:
            confidence = 0.0
            
            # امتیاز تشخیص ماینر
            if mining_detection:
                max_crypto_score = max([crypto['score'] for crypto in mining_detection.values()])
                confidence += max_crypto_score * 0.6
            
            # امتیاز ویژگی‌های طیفی
            if 'error' not in spectral_features:
                # بررسی ویژگی‌های غیرعادی
                spectral_score = 0.0
                
                # MFCC تنوع
                if 'mfcc_std' in spectral_features:
                    mfcc_variation = np.mean(spectral_features['mfcc_std'])
                    if mfcc_variation > 0.5:
                        spectral_score += 0.2
                
                # مرکز طیفی
                if 'spectral_centroid_mean' in spectral_features:
                    centroid = spectral_features['spectral_centroid_mean']
                    if 1000 < centroid < 8000:  # محدوده ماینر
                        spectral_score += 0.15
                
                # پهنای باند طیفی
                if 'spectral_bandwidth_mean' in spectral_features:
                    bandwidth = spectral_features['spectral_bandwidth_mean']
                    if bandwidth > 2000:  # پهنای باند بالا
                        spectral_score += 0.15
                
                # ریتم
                if 'tempo' in spectral_features:
                    tempo = spectral_features['tempo']
                    if 60 < tempo < 180:  # ریتم طبیعی
                        spectral_score += 0.1
                
                confidence += spectral_score
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"خطا در محاسبه امتیاز اطمینان: {e}")
            return 0.0
    
    def advanced_thermal_analysis(self, thermal_data: np.ndarray) -> Dict[str, Any]:
        """تحلیل پیشرفته حرارتی"""
        try:
            # تحلیل الگوهای حرارتی
            thermal_patterns = self.analyze_thermal_patterns(thermal_data)
            
            # تشخیص آنومالی‌های حرارتی
            anomalies = self.detect_thermal_anomalies(thermal_data)
            
            # تحلیل الگوهای ماینر
            mining_analysis = self.analyze_mining_thermal_patterns(thermal_data)
            
            # محاسبه امتیاز اطمینان
            confidence_score = self.calculate_thermal_confidence(thermal_patterns, anomalies, mining_analysis)
            
            return {
                'detection_type': 'advanced_thermal',
                'thermal_patterns': thermal_patterns,
                'anomalies': anomalies,
                'mining_analysis': mining_analysis,
                'confidence_score': confidence_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f"تحلیل حرارتی پیشرفته ناموفق: {str(e)}"}
    
    def analyze_thermal_patterns(self, thermal_data: np.ndarray) -> Dict[str, Any]:
        """تحلیل الگوهای حرارتی"""
        try:
            # آمار پایه
            max_temp = np.max(thermal_data)
            min_temp = np.min(thermal_data)
            mean_temp = np.mean(thermal_data)
            std_temp = np.std(thermal_data)
            
            # گرادیان حرارتی
            grad_x = np.gradient(thermal_data, axis=1)
            grad_y = np.gradient(thermal_data, axis=0)
            grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # نقاط داغ
            hot_spots = thermal_data > (mean_temp + 2 * std_temp)
            hot_spot_count = np.sum(hot_spots)
            hot_spot_area = hot_spot_count / thermal_data.size
            
            # الگوهای خطی (ممکن است نشان‌دهنده ماینر باشد)
            linear_patterns = self.detect_linear_thermal_patterns(thermal_data)
            
            return {
                'statistics': {
                    'max_temperature': float(max_temp),
                    'min_temperature': float(min_temp),
                    'mean_temperature': float(mean_temp),
                    'std_temperature': float(std_temp)
                },
                'gradients': {
                    'max_gradient': float(np.max(grad_magnitude)),
                    'mean_gradient': float(np.mean(grad_magnitude)),
                    'gradient_variation': float(np.std(grad_magnitude))
                },
                'hot_spots': {
                    'count': int(hot_spot_count),
                    'area_ratio': float(hot_spot_area),
                    'max_hot_spot_temp': float(np.max(thermal_data[hot_spots])) if hot_spot_count > 0 else 0
                },
                'linear_patterns': linear_patterns
            }
            
        except Exception as e:
            return {'error': f"تحلیل الگوهای حرارتی ناموفق: {str(e)}"}
    
    def detect_linear_thermal_patterns(self, thermal_data: np.ndarray) -> List[Dict[str, Any]]:
        """تشخیص الگوهای خطی حرارتی"""
        try:
            patterns = []
            
            # استفاده از تبدیل Hough برای تشخیص خطوط
            edges = cv2.Canny(thermal_data.astype(np.uint8), 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            if lines is not None:
                for line in lines:
                    rho, theta = line[0]
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    
                    x1 = int(x0 + 1000 * (-b))
                    y1 = int(y0 + 1000 * (a))
                    x2 = int(x0 - 1000 * (-b))
                    y2 = int(y0 - 1000 * (a))
                    
                    # محاسبه طول خط
                    length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    
                    if length > 20:  # خطوط طولانی‌تر
                        patterns.append({
                            'start': (x1, y1),
                            'end': (x2, y2),
                            'length': float(length),
                            'angle': float(theta * 180 / np.pi)
                        })
            
            return patterns
            
        except Exception as e:
            print(f"خطا در تشخیص الگوهای خطی حرارتی: {e}")
            return []
    
    def detect_thermal_anomalies(self, thermal_data: np.ndarray) -> Dict[str, Any]:
        """تشخیص آنومالی‌های حرارتی"""
        try:
            # آمار پایه
            mean_temp = np.mean(thermal_data)
            std_temp = np.std(thermal_data)
            
            # نقاط آنومال
            anomaly_threshold = mean_temp + 3 * std_temp
            anomalies = thermal_data > anomaly_threshold
            
            # خوشه‌بندی آنومالی‌ها
            anomaly_clusters = self.cluster_anomalies(thermal_data, anomalies)
            
            # محاسبه امتیاز آنومالی
            anomaly_score = np.sum(anomalies) / thermal_data.size
            
            return {
                'anomaly_threshold': float(anomaly_threshold),
                'anomaly_count': int(np.sum(anomalies)),
                'anomaly_ratio': float(anomaly_score),
                'anomaly_clusters': anomaly_clusters,
                'severity': 'high' if anomaly_score > 0.1 else 'medium' if anomaly_score > 0.05 else 'low'
            }
            
        except Exception as e:
            return {'error': f"تشخیص آنومالی‌های حرارتی ناموفق: {str(e)}"}
    
    def cluster_anomalies(self, thermal_data: np.ndarray, anomalies: np.ndarray) -> List[Dict[str, Any]]:
        """خوشه‌بندی آنومالی‌ها"""
        try:
            clusters = []
            
            # یافتن نقاط آنومال
            anomaly_coords = np.where(anomalies)
            
            if len(anomaly_coords[0]) > 0:
                # ساده‌سازی: گروه‌بندی بر اساس فاصله
                coords = list(zip(anomaly_coords[0], anomaly_coords[1]))
                
                while coords:
                    cluster = [coords.pop(0)]
                    i = 0
                    
                    while i < len(coords):
                        coord = coords[i]
                        # بررسی فاصله از مرکز خوشه
                        center = np.mean(cluster, axis=0)
                        distance = np.sqrt(np.sum((coord - center)**2))
                        
                        if distance < 10:  # فاصله آستانه
                            cluster.append(coords.pop(i))
                        else:
                            i += 1
                    
                    if len(cluster) > 1:  # خوشه‌های معنی‌دار
                        cluster_coords = np.array(cluster)
                        cluster_temp = thermal_data[cluster_coords[:, 0], cluster_coords[:, 1]]
                        
                        clusters.append({
                            'size': len(cluster),
                            'center': (float(np.mean(cluster_coords[:, 1])), float(np.mean(cluster_coords[:, 0]))),
                            'max_temperature': float(np.max(cluster_temp)),
                            'mean_temperature': float(np.mean(cluster_temp)),
                            'area': len(cluster)
                        })
            
            return clusters
            
        except Exception as e:
            print(f"خطا در خوشه‌بندی آنومالی‌ها: {e}")
            return []
    
    def analyze_mining_thermal_patterns(self, thermal_data: np.ndarray) -> Dict[str, Any]:
        """تحلیل الگوهای حرارتی ماینر"""
        try:
            mining_indicators = {}
            
            for crypto_type, patterns in self.mining_patterns.items():
                crypto_score = 0
                detected_features = []
                
                # بررسی محدوده دمایی
                thermal_pattern = patterns['thermal']
                temp_range = thermal_pattern['temp_range']
                
                max_temp = np.max(thermal_data)
                if temp_range[0] <= max_temp <= temp_range[1]:
                    crypto_score += 0.4
                    detected_features.append(f"temp_range_{temp_range[0]}-{temp_range[1]}")
                
                # بررسی الگوهای حرارتی
                for pattern in thermal_pattern['patterns']:
                    if self.detect_mining_thermal_pattern(pattern, thermal_data):
                        crypto_score += 0.3
                        detected_features.append(pattern)
                
                # بررسی توزیع حرارتی
                temp_distribution = self.analyze_temperature_distribution(thermal_data)
                if self.is_mining_temperature_distribution(temp_distribution):
                    crypto_score += 0.3
                    detected_features.append("mining_distribution")
                
                if crypto_score > 0:
                    mining_indicators[crypto_type] = {
                        'score': crypto_score,
                        'features': detected_features,
                        'confidence': min(crypto_score, 1.0)
                    }
            
            return mining_indicators
            
        except Exception as e:
            return {'error': f"تحلیل الگوهای حرارتی ماینر ناموفق: {str(e)}"}
    
    def detect_mining_thermal_pattern(self, pattern: str, thermal_data: np.ndarray) -> bool:
        """تشخیص الگوی حرارتی خاص ماینر"""
        try:
            if pattern == 'gpu_cluster':
                # الگوی خوشه GPU - نقاط داغ منظم
                hot_spots = thermal_data > np.percentile(thermal_data, 90)
                if np.sum(hot_spots) > 0:
                    # بررسی منظم بودن نقاط داغ
                    hot_coords = np.where(hot_spots)
                    if len(hot_coords[0]) > 3:
                        # محاسبه فاصله بین نقاط داغ
                        distances = []
                        for i in range(len(hot_coords[0])):
                            for j in range(i+1, len(hot_coords[0])):
                                dist = np.sqrt((hot_coords[0][i] - hot_coords[0][j])**2 + 
                                            (hot_coords[1][i] - hot_coords[1][j])**2)
                                distances.append(dist)
                        
                        if distances:
                            mean_dist = np.mean(distances)
                            std_dist = np.std(distances)
                            regularity = std_dist / mean_dist if mean_dist > 0 else 1
                            return regularity < 0.5  # منظم بودن
                
            elif pattern == 'asic_array':
                # الگوی آرایه ASIC - الگوی منظم و تکراری
                # استفاده از تبدیل فوریه برای تشخیص الگوهای تکراری
                fft_thermal = np.fft.fft2(thermal_data)
                fft_magnitude = np.abs(fft_thermal)
                
                # یافتن قله‌های قوی در FFT
                peaks = signal.find_peaks(fft_magnitude.flatten(), height=np.max(fft_magnitude)*0.3)
                if len(peaks[0]) > 5:  # الگوی پیچیده
                    return True
                
            elif pattern == 'memory_intensive':
                # الگوی حافظه - توزیع حرارتی یکنواخت
                temp_std = np.std(thermal_data)
                temp_mean = np.mean(thermal_data)
                uniformity = temp_std / temp_mean if temp_mean > 0 else 1
                return uniformity < 0.3  # یکنواختی بالا
                
            elif pattern == 'compute_units':
                # الگوی واحدهای محاسباتی - نقاط داغ مجزا
                hot_spots = thermal_data > np.percentile(thermal_data, 85)
                if np.sum(hot_spots) > 0:
                    # بررسی مجزا بودن نقاط داغ
                    hot_coords = np.where(hot_spots)
                    if len(hot_coords[0]) > 2:
                        # محاسبه فاصله بین نقاط داغ
                        min_distance = float('inf')
                        for i in range(len(hot_coords[0])):
                            for j in range(i+1, len(hot_coords[0])):
                                dist = np.sqrt((hot_coords[0][i] - hot_coords[0][j])**2 + 
                                            (hot_coords[1][i] - hot_coords[1][j])**2)
                                min_distance = min(min_distance, dist)
                        
                        return min_distance > 20  # فاصله کافی
                
        except Exception as e:
            print(f"خطا در تشخیص الگوی حرارتی {pattern}: {e}")
            
        return False
    
    def analyze_temperature_distribution(self, thermal_data: np.ndarray) -> Dict[str, float]:
        """تحلیل توزیع دمایی"""
        try:
            # آمار توزیع
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            percentile_values = np.percentile(thermal_data, percentiles)
            
            # توزیع نرمال
            mean_temp = np.mean(thermal_data)
            std_temp = np.std(thermal_data)
            
            # چولگی و کشیدگی
            skewness = self.calculate_skewness(thermal_data)
            kurtosis = self.calculate_kurtosis(thermal_data)
            
            return {
                'percentiles': dict(zip(percentiles, percentile_values.tolist())),
                'mean': float(mean_temp),
                'std': float(std_temp),
                'skewness': float(skewness),
                'kurtosis': float(kurtosis),
                'range': float(np.max(thermal_data) - np.min(thermal_data))
            }
            
        except Exception as e:
            return {'error': f"تحلیل توزیع دمایی ناموفق: {str(e)}"}
    
    def calculate_skewness(self, data: np.ndarray) -> float:
        """محاسبه چولگی"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return np.mean(((data - mean) / std) ** 3)
        except:
            return 0
    
    def calculate_kurtosis(self, data: np.ndarray) -> float:
        """محاسبه کشیدگی"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0
            return np.mean(((data - mean) / std) ** 4) - 3
        except:
            return 0
    
    def is_mining_temperature_distribution(self, distribution: Dict[str, float]) -> bool:
        """بررسی آیا توزیع دمایی نشان‌دهنده ماینر است"""
        try:
            if 'error' in distribution:
                return False
            
            # معیارهای توزیع ماینر
            criteria = 0
            
            # چولگی مثبت (دمای بالا)
            if distribution.get('skewness', 0) > 0.5:
                criteria += 1
            
            # کشیدگی بالا (تمرکز در دمای خاص)
            if distribution.get('kurtosis', 0) > 2:
                criteria += 1
            
            # محدوده دمایی وسیع
            if distribution.get('range', 0) > 30:
                criteria += 1
            
            # درصد بالای دماهای بالا
            if distribution.get('percentiles', {}).get(95, 0) > 60:
                criteria += 1
            
            return criteria >= 2  # حداقل 2 معیار
            
        except Exception as e:
            print(f"خطا در بررسی توزیع دمایی ماینر: {e}")
            return False
    
    def calculate_thermal_confidence(self, thermal_patterns: Dict[str, Any], 
                                   anomalies: Dict[str, Any], 
                                   mining_analysis: Dict[str, Any]) -> float:
        """محاسبه امتیاز اطمینان تحلیل حرارتی"""
        try:
            confidence = 0.0
            
            # امتیاز الگوهای حرارتی
            if 'error' not in thermal_patterns:
                # نقاط داغ
                hot_spot_ratio = thermal_patterns.get('hot_spots', {}).get('area_ratio', 0)
                if hot_spot_ratio > 0.05:  # بیش از 5% نقاط داغ
                    confidence += 0.3
                
                # گرادیان حرارتی
                max_gradient = thermal_patterns.get('gradients', {}).get('max_gradient', 0)
                if max_gradient > 10:  # گرادیان قوی
                    confidence += 0.2
                
                # الگوهای خطی
                linear_patterns = thermal_patterns.get('linear_patterns', [])
                if len(linear_patterns) > 2:  # الگوهای خطی متعدد
                    confidence += 0.2
            
            # امتیاز آنومالی‌ها
            if 'error' not in anomalies:
                anomaly_ratio = anomalies.get('anomaly_ratio', 0)
                if anomaly_ratio > 0.01:  # بیش از 1% آنومالی
                    confidence += 0.2
                
                severity = anomalies.get('severity', 'low')
                if severity == 'high':
                    confidence += 0.1
            
            # امتیاز تحلیل ماینر
            if mining_analysis:
                max_crypto_score = max([crypto['score'] for crypto in mining_analysis.values()])
                confidence += max_crypto_score * 0.3
            
            return min(confidence, 1.0)
            
        except Exception as e:
            print(f"خطا در محاسبه امتیاز اطمینان حرارتی: {e}")
            return 0.0

def main():
    """تابع اصلی برای تست"""
    detector = AdvancedMiningDetector()
    
    print("🔍 SHBHHBSH Advanced - ماژول پیشرفته تشخیص ماینر")
    print("=" * 60)
    
    # تست تحلیل صوتی
    print("\n📊 تست تحلیل صوتی پیشرفته...")
    
    # تولید داده صوتی شبیه‌سازی شده
    sample_rate = 44100
    duration = 5
    t = np.linspace(0, duration, sample_rate * duration)
    
    # سیگنال ماینر شبیه‌سازی شده
    mining_signal = (
        np.sin(2 * np.pi * 100 * t) * 0.3 +  # فرکانس پایه
        np.sin(2 * np.pi * 200 * t) * 0.2 +  # هارمونیک اول
        np.sin(2 * np.pi * 400 * t) * 0.15 + # هارمونیک دوم
        np.sin(2 * np.pi * 800 * t) * 0.1 +  # هارمونیک سوم
        np.random.normal(0, 0.05, len(t))     # نویز
    )
    
    # تحلیل پیشرفته
    result = detector.advanced_acoustic_analysis(mining_signal, sample_rate)
    
    if 'error' not in result:
        print(f"✅ تحلیل صوتی تکمیل شد")
        print(f"🔊 امتیاز اطمینان: {result['confidence_score']:.3f}")
        
        if result['mining_detection']:
            print("🎯 تشخیص ماینر:")
            for crypto, info in result['mining_detection'].items():
                print(f"   {crypto}: {info['confidence']:.3f}")
    else:
        print(f"❌ خطا در تحلیل صوتی: {result['error']}")
    
    # تست تحلیل حرارتی
    print("\n🌡️ تست تحلیل حرارتی پیشرفته...")
    
    # تولید داده حرارتی شبیه‌سازی شده
    thermal_width, thermal_height = 320, 240
    thermal_data = np.random.normal(25, 5, (thermal_height, thermal_width))
    
    # اضافه کردن الگوهای ماینر
    center_x, center_y = thermal_width // 2, thermal_height // 2
    
    # خوشه GPU
    for y in range(thermal_height):
        for x in range(thermal_width):
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < 80:  # ناحیه ماینر
                if distance < 40:  # هسته داغ
                    thermal_data[y, x] = 75 + np.random.normal(0, 3)
                elif distance < 60:  # ناحیه گرم
                    thermal_data[y, x] = 60 + np.random.normal(0, 5)
                else:  # ناحیه گرم ملایم
                    thermal_data[y, x] = 45 + np.random.normal(0, 4)
    
    # تحلیل پیشرفته حرارتی
    thermal_result = detector.advanced_thermal_analysis(thermal_data)
    
    if 'error' not in thermal_result:
        print(f"✅ تحلیل حرارتی تکمیل شد")
        print(f"🌡️ امتیاز اطمینان: {thermal_result['confidence_score']:.3f}")
        
        if thermal_result['mining_analysis']:
            print("🎯 تحلیل ماینر حرارتی:")
            for crypto, info in thermal_result['mining_analysis'].items():
                print(f"   {crypto}: {info['confidence']:.3f}")
    else:
        print(f"❌ خطا در تحلیل حرارتی: {thermal_result['error']}")
    
    print("\n🎉 تست ماژول پیشرفته تکمیل شد!")

if __name__ == "__main__":
    main()