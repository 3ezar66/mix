 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Analytics and Prediction System
سیستم تحلیل هوشمند و پیش‌بینی
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import aiosqlite
from dataclasses import dataclass
from enum import Enum
import joblib
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Analysis types"""
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    PREDICTION = "prediction"
    CLUSTERING = "clustering"
    TREND_ANALYSIS = "trend_analysis"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class AnalysisResult:
    """Analysis result data structure"""
    id: str
    type: AnalysisType
    timestamp: datetime
    data: Dict[str, Any]
    confidence: float
    insights: List[str]
    recommendations: List[str]
    visualizations: Dict[str, str]

class AIAnalyticsSystem:
    """
    سیستم تحلیل هوشمند و پیش‌بینی
    """
    
    def __init__(self, db_path: str = "ilam_mining.db"):
        self.db_path = db_path
        self.models = {}
        self.scalers = {}
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI/ML models"""
        # Anomaly detection model
        self.models['anomaly_detector'] = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        # Pattern recognition model
        self.models['pattern_classifier'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        # Clustering model
        self.models['device_clusterer'] = DBSCAN(
            eps=0.5,
            min_samples=5
        )
        
        # Trend analysis model
        self.models['trend_predictor'] = RandomForestClassifier(
            n_estimators=50,
            random_state=42
        )
        
        # Risk assessment model
        self.models['risk_assessor'] = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        
        # Initialize scalers
        self.scalers['standard'] = StandardScaler()
        self.scalers['pca'] = PCA(n_components=3)
        
        logger.info("AI models initialized successfully")
    
    async def get_database_connection(self):
        """Get database connection"""
        return await aiosqlite.connect(self.db_path)
    
    async def analyze_network_patterns(self) -> AnalysisResult:
        """Analyze network patterns for mining detection"""
        async with await self.get_database_connection() as db:
            # Fetch network data
            query = """
            SELECT 
                ip_address,
                mac_address,
                power_consumption,
                confidence_score,
                threat_level,
                detection_methods,
                created_at,
                last_seen
            FROM detected_miners
            WHERE created_at >= datetime('now', '-30 days')
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                return self._create_empty_result(AnalysisType.PATTERN_RECOGNITION)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'ip_address', 'mac_address', 'power_consumption', 'confidence_score',
                'threat_level', 'detection_methods', 'created_at', 'last_seen'
            ])
            
            # Feature engineering
            features = self._extract_network_features(df)
            
            # Pattern analysis
            patterns = self._analyze_patterns(features)
            
            # Generate insights
            insights = self._generate_network_insights(df, patterns)
            
            # Generate recommendations
            recommendations = self._generate_network_recommendations(patterns)
            
            # Create visualizations
            visualizations = await self._create_network_visualizations(df, patterns)
            
            return AnalysisResult(
                id=f"network_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=AnalysisType.PATTERN_RECOGNITION,
                timestamp=datetime.now(),
                data=patterns,
                confidence=patterns.get('confidence', 0.8),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
    
    async def detect_anomalies(self) -> AnalysisResult:
        """Detect anomalies in mining activities"""
        async with await self.get_database_connection() as db:
            # Fetch recent data
            query = """
            SELECT 
                power_consumption,
                confidence_score,
                threat_level,
                created_at,
                detection_count
            FROM detected_miners
            WHERE created_at >= datetime('now', '-7 days')
            ORDER BY created_at
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                return self._create_empty_result(AnalysisType.ANOMALY_DETECTION)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'power_consumption', 'confidence_score', 'threat_level',
                'created_at', 'detection_count'
            ])
            
            # Prepare features for anomaly detection
            features = self._prepare_anomaly_features(df)
            
            # Detect anomalies
            anomalies = self._detect_anomalies_in_data(features)
            
            # Generate insights
            insights = self._generate_anomaly_insights(df, anomalies)
            
            # Generate recommendations
            recommendations = self._generate_anomaly_recommendations(anomalies)
            
            # Create visualizations
            visualizations = await self._create_anomaly_visualizations(df, anomalies)
            
            return AnalysisResult(
                id=f"anomaly_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=AnalysisType.ANOMALY_DETECTION,
                timestamp=datetime.now(),
                data=anomalies,
                confidence=anomalies.get('confidence', 0.85),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
    
    async def predict_future_activities(self, days_ahead: int = 7) -> AnalysisResult:
        """Predict future mining activities"""
        async with await self.get_database_connection() as db:
            # Fetch historical data
            query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as daily_detections,
                SUM(power_consumption) as daily_power,
                AVG(confidence_score) as avg_confidence
            FROM detected_miners
            WHERE created_at >= datetime('now', '-90 days')
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                return self._create_empty_result(AnalysisType.PREDICTION)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=['date', 'daily_detections', 'daily_power', 'avg_confidence'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Prepare time series data
            time_series = self._prepare_time_series_data(df)
            
            # Make predictions
            predictions = self._predict_future_values(time_series, days_ahead)
            
            # Generate insights
            insights = self._generate_prediction_insights(predictions)
            
            # Generate recommendations
            recommendations = self._generate_prediction_recommendations(predictions)
            
            # Create visualizations
            visualizations = await self._create_prediction_visualizations(df, predictions)
            
            return AnalysisResult(
                id=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=AnalysisType.PREDICTION,
                timestamp=datetime.now(),
                data=predictions,
                confidence=predictions.get('confidence', 0.75),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
    
    async def cluster_devices(self) -> AnalysisResult:
        """Cluster devices based on characteristics"""
        async with await self.get_database_connection() as db:
            # Fetch device data
            query = """
            SELECT 
                power_consumption,
                confidence_score,
                threat_level,
                detection_count,
                device_type
            FROM detected_miners
            WHERE created_at >= datetime('now', '-30 days')
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                return self._create_empty_result(AnalysisType.CLUSTERING)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'power_consumption', 'confidence_score', 'threat_level',
                'detection_count', 'device_type'
            ])
            
            # Prepare clustering features
            features = self._prepare_clustering_features(df)
            
            # Perform clustering
            clusters = self._perform_clustering(features)
            
            # Generate insights
            insights = self._generate_clustering_insights(df, clusters)
            
            # Generate recommendations
            recommendations = self._generate_clustering_recommendations(clusters)
            
            # Create visualizations
            visualizations = await self._create_clustering_visualizations(df, clusters)
            
            return AnalysisResult(
                id=f"clustering_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=AnalysisType.CLUSTERING,
                timestamp=datetime.now(),
                data=clusters,
                confidence=clusters.get('confidence', 0.8),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
    
    async def assess_risk_levels(self) -> AnalysisResult:
        """Assess risk levels for different areas"""
        async with await self.get_database_connection() as db:
            # Fetch risk assessment data
            query = """
            SELECT 
                city,
                region,
                COUNT(*) as device_count,
                SUM(power_consumption) as total_power,
                AVG(confidence_score) as avg_confidence,
                COUNT(CASE WHEN threat_level = 'critical' THEN 1 END) as critical_count,
                COUNT(CASE WHEN threat_level = 'high' THEN 1 END) as high_count
            FROM detected_miners
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY city, region
            """
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
            
            if not rows:
                return self._create_empty_result(AnalysisType.RISK_ASSESSMENT)
            
            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=[
                'city', 'region', 'device_count', 'total_power', 'avg_confidence',
                'critical_count', 'high_count'
            ])
            
            # Calculate risk scores
            risk_scores = self._calculate_risk_scores(df)
            
            # Generate insights
            insights = self._generate_risk_insights(df, risk_scores)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_scores)
            
            # Create visualizations
            visualizations = await self._create_risk_visualizations(df, risk_scores)
            
            return AnalysisResult(
                id=f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                type=AnalysisType.RISK_ASSESSMENT,
                timestamp=datetime.now(),
                data=risk_scores,
                confidence=risk_scores.get('confidence', 0.85),
                insights=insights,
                recommendations=recommendations,
                visualizations=visualizations
            )
    
    def _extract_network_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract network features for pattern analysis"""
        features = {
            'total_devices': len(df),
            'avg_power_consumption': df['power_consumption'].mean(),
            'avg_confidence': df['confidence_score'].mean(),
            'threat_distribution': df['threat_level'].value_counts().to_dict(),
            'detection_methods': self._extract_detection_methods(df),
            'temporal_patterns': self._extract_temporal_patterns(df),
            'power_distribution': {
                'min': df['power_consumption'].min(),
                'max': df['power_consumption'].max(),
                'std': df['power_consumption'].std(),
                'percentiles': df['power_consumption'].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        }
        
        return features
    
    def _extract_detection_methods(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract detection methods distribution"""
        methods = []
        for method_str in df['detection_methods']:
            if method_str:
                try:
                    method_list = json.loads(method_str)
                    methods.extend(method_list)
                except:
                    continue
        
        return pd.Series(methods).value_counts().to_dict()
    
    def _extract_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract temporal patterns from data"""
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        
        return {
            'hourly_distribution': df['hour'].value_counts().sort_index().to_dict(),
            'daily_distribution': df['day_of_week'].value_counts().sort_index().to_dict(),
            'peak_hours': df['hour'].value_counts().head(3).index.tolist(),
            'peak_days': df['day_of_week'].value_counts().head(3).index.tolist()
        }
    
    def _analyze_patterns(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in network data"""
        patterns = {
            'confidence': 0.8,
            'patterns_found': [],
            'anomalies_detected': [],
            'trends_identified': []
        }
        
        # Analyze power consumption patterns
        if features['avg_power_consumption'] > 3000:
            patterns['patterns_found'].append("مصرف برق بالا در شبکه")
        
        # Analyze threat distribution
        critical_count = features['threat_distribution'].get('critical', 0)
        if critical_count > 0:
            patterns['anomalies_detected'].append(f"{critical_count} دستگاه با تهدید بحرانی")
        
        # Analyze temporal patterns
        peak_hours = features['temporal_patterns']['peak_hours']
        if 22 in peak_hours or 23 in peak_hours or 0 in peak_hours:
            patterns['patterns_found'].append("فعالیت شبانه غیرعادی")
        
        return patterns
    
    def _prepare_anomaly_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection"""
        # Convert threat levels to numeric
        threat_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        df['threat_numeric'] = df['threat_level'].map(threat_mapping)
        
        # Select features for anomaly detection
        features = df[['power_consumption', 'confidence_score', 'threat_numeric', 'detection_count']].values
        
        # Handle missing values
        features = np.nan_to_num(features, nan=0)
        
        return features
    
    def _detect_anomalies_in_data(self, features: np.ndarray) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        # Fit anomaly detection model
        model = self.models['anomaly_detector']
        model.fit(features)
        
        # Predict anomalies
        predictions = model.predict(features)
        anomaly_scores = model.decision_function(features)
        
        # Identify anomalies (predictions == -1)
        anomalies = {
            'confidence': 0.85,
            'total_samples': len(features),
            'anomaly_count': np.sum(predictions == -1),
            'anomaly_percentage': (np.sum(predictions == -1) / len(features)) * 100,
            'anomaly_scores': anomaly_scores.tolist(),
            'anomaly_indices': np.where(predictions == -1)[0].tolist()
        }
        
        return anomalies
    
    def _prepare_time_series_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare time series data for prediction"""
        # Set date as index
        df = df.set_index('date')
        
        # Resample to daily frequency and fill missing values
        df = df.resample('D').mean().fillna(0)
        
        # Create lag features
        for lag in [1, 2, 3, 7]:
            df[f'daily_detections_lag_{lag}'] = df['daily_detections'].shift(lag)
            df[f'daily_power_lag_{lag}'] = df['daily_power'].shift(lag)
        
        # Create rolling features
        for window in [3, 7, 14]:
            df[f'daily_detections_rolling_mean_{window}'] = df['daily_detections'].rolling(window=window).mean()
            df[f'daily_power_rolling_mean_{window}'] = df['daily_power'].rolling(window=window).mean()
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def _predict_future_values(self, time_series: pd.DataFrame, days_ahead: int) -> Dict[str, Any]:
        """Predict future values"""
        # Prepare features for prediction
        feature_columns = [col for col in time_series.columns if 'lag' in col or 'rolling' in col]
        X = time_series[feature_columns].values
        y_detections = time_series['daily_detections'].values
        y_power = time_series['daily_power'].values
        
        # Train prediction models
        model_detections = self.models['trend_predictor']
        model_power = RandomForestClassifier(n_estimators=50, random_state=42)
        
        model_detections.fit(X, y_detections)
        model_power.fit(X, y_power)
        
        # Make predictions for future days
        future_predictions = {
            'confidence': 0.75,
            'predictions': []
        }
        
        last_features = X[-1:].copy()
        
        for day in range(1, days_ahead + 1):
            # Predict detections and power
            pred_detections = model_detections.predict(last_features)[0]
            pred_power = model_power.predict(last_features)[0]
            
            future_date = datetime.now() + timedelta(days=day)
            
            future_predictions['predictions'].append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_detections': int(pred_detections),
                'predicted_power': float(pred_power),
                'confidence': 0.75
            })
            
            # Update features for next prediction
            # This is a simplified approach - in practice, you'd need more sophisticated time series modeling
        
        return future_predictions
    
    def _prepare_clustering_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for clustering"""
        # Convert categorical variables
        threat_mapping = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        df['threat_numeric'] = df['threat_level'].map(threat_mapping)
        
        # Select features for clustering
        features = df[['power_consumption', 'confidence_score', 'threat_numeric', 'detection_count']].values
        
        # Scale features
        features_scaled = self.scalers['standard'].fit_transform(features)
        
        return features_scaled
    
    def _perform_clustering(self, features: np.ndarray) -> Dict[str, Any]:
        """Perform clustering on device data"""
        # Perform clustering
        model = self.models['device_clusterer']
        cluster_labels = model.fit_predict(features)
        
        # Analyze clusters
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        
        clusters = {
            'confidence': 0.8,
            'n_clusters': n_clusters,
            'cluster_labels': cluster_labels.tolist(),
            'cluster_sizes': np.bincount(cluster_labels[cluster_labels >= 0]).tolist(),
            'noise_points': np.sum(cluster_labels == -1)
        }
        
        return clusters
    
    def _calculate_risk_scores(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate risk scores for different areas"""
        risk_scores = {
            'confidence': 0.85,
            'areas': []
        }
        
        for _, row in df.iterrows():
            # Calculate risk score based on multiple factors
            device_risk = row['device_count'] * 0.3
            power_risk = (row['total_power'] / 1000) * 0.4  # Convert to kW
            critical_risk = row['critical_count'] * 0.5
            high_risk = row['high_count'] * 0.3
            
            total_risk = device_risk + power_risk + critical_risk + high_risk
            
            # Normalize risk score (0-100)
            normalized_risk = min(total_risk * 10, 100)
            
            # Determine risk level
            if normalized_risk >= 80:
                risk_level = 'critical'
            elif normalized_risk >= 60:
                risk_level = 'high'
            elif normalized_risk >= 40:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            risk_scores['areas'].append({
                'city': row['city'],
                'region': row['region'],
                'risk_score': round(normalized_risk, 2),
                'risk_level': risk_level,
                'device_count': row['device_count'],
                'total_power': row['total_power'],
                'critical_count': row['critical_count'],
                'high_count': row['high_count']
            })
        
        # Sort by risk score
        risk_scores['areas'].sort(key=lambda x: x['risk_score'], reverse=True)
        
        return risk_scores
    
    def _generate_network_insights(self, df: pd.DataFrame, patterns: Dict[str, Any]) -> List[str]:
        """Generate insights from network pattern analysis"""
        insights = []
        
        total_devices = len(df)
        avg_power = df['power_consumption'].mean()
        
        insights.append(f"تعداد کل دستگاه‌های تشخیص داده شده: {total_devices}")
        insights.append(f"متوسط مصرف برق: {avg_power:.0f} وات")
        
        if patterns['patterns_found']:
            insights.extend(patterns['patterns_found'])
        
        if patterns['anomalies_detected']:
            insights.extend(patterns['anomalies_detected'])
        
        return insights
    
    def _generate_anomaly_insights(self, df: pd.DataFrame, anomalies: Dict[str, Any]) -> List[str]:
        """Generate insights from anomaly detection"""
        insights = []
        
        anomaly_count = anomalies['anomaly_count']
        total_samples = anomalies['total_samples']
        anomaly_percentage = anomalies['anomaly_percentage']
        
        insights.append(f"تعداد ناهنجاری‌های تشخیص داده شده: {anomaly_count}")
        insights.append(f"درصد ناهنجاری‌ها: {anomaly_percentage:.1f}%")
        
        if anomaly_percentage > 10:
            insights.append("سطح بالای ناهنجاری در شبکه تشخیص داده شد")
        
        return insights
    
    def _generate_prediction_insights(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate insights from predictions"""
        insights = []
        
        pred_list = predictions['predictions']
        if pred_list:
            avg_detections = np.mean([p['predicted_detections'] for p in pred_list])
            avg_power = np.mean([p['predicted_power'] for p in pred_list])
            
            insights.append(f"پیش‌بینی متوسط تشخیص‌های روزانه: {avg_detections:.1f}")
            insights.append(f"پیش‌بینی متوسط مصرف برق روزانه: {avg_power:.0f} وات")
            
            # Trend analysis
            first_pred = pred_list[0]
            last_pred = pred_list[-1]
            
            if last_pred['predicted_detections'] > first_pred['predicted_detections']:
                insights.append("روند افزایشی در تشخیص‌ها پیش‌بینی می‌شود")
            elif last_pred['predicted_detections'] < first_pred['predicted_detections']:
                insights.append("روند کاهشی در تشخیص‌ها پیش‌بینی می‌شود")
            else:
                insights.append("روند ثابت در تشخیص‌ها پیش‌بینی می‌شود")
        
        return insights
    
    def _generate_clustering_insights(self, df: pd.DataFrame, clusters: Dict[str, Any]) -> List[str]:
        """Generate insights from clustering analysis"""
        insights = []
        
        n_clusters = clusters['n_clusters']
        noise_points = clusters['noise_points']
        
        insights.append(f"تعداد خوشه‌های شناسایی شده: {n_clusters}")
        insights.append(f"تعداد نقاط نویز: {noise_points}")
        
        if n_clusters > 1:
            insights.append("انواع مختلفی از دستگاه‌ها در شبکه شناسایی شد")
        
        if noise_points > 0:
            insights.append("دستگاه‌های غیرعادی در شبکه شناسایی شد")
        
        return insights
    
    def _generate_risk_insights(self, df: pd.DataFrame, risk_scores: Dict[str, Any]) -> List[str]:
        """Generate insights from risk assessment"""
        insights = []
        
        areas = risk_scores['areas']
        if areas:
            high_risk_areas = [area for area in areas if area['risk_level'] in ['high', 'critical']]
            critical_areas = [area for area in areas if area['risk_level'] == 'critical']
            
            insights.append(f"تعداد مناطق پرخطر: {len(high_risk_areas)}")
            insights.append(f"تعداد مناطق بحرانی: {len(critical_areas)}")
            
            if critical_areas:
                top_critical = critical_areas[0]
                insights.append(f"منطقه با بالاترین ریسک: {top_critical['city']} - {top_critical['region']}")
        
        return insights
    
    def _generate_network_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations from network analysis"""
        recommendations = []
        
        if "مصرف برق بالا در شبکه" in patterns['patterns_found']:
            recommendations.append("بررسی دقیق‌تر شبکه برق در مناطق مشکوک")
        
        if "فعالیت شبانه غیرعادی" in patterns['patterns_found']:
            recommendations.append("گشت‌زنی شبانه در مناطق مشکوک")
        
        if patterns['anomalies_detected']:
            recommendations.append("بررسی فوری دستگاه‌های با تهدید بحرانی")
        
        return recommendations
    
    def _generate_anomaly_recommendations(self, anomalies: Dict[str, Any]) -> List[str]:
        """Generate recommendations from anomaly detection"""
        recommendations = []
        
        anomaly_percentage = anomalies['anomaly_percentage']
        
        if anomaly_percentage > 10:
            recommendations.append("افزایش نظارت بر شبکه")
            recommendations.append("بررسی دقیق‌تر دستگاه‌های مشکوک")
        
        if anomalies['anomaly_count'] > 0:
            recommendations.append("تحلیل عمیق ناهنجاری‌های شناسایی شده")
        
        return recommendations
    
    def _generate_prediction_recommendations(self, predictions: Dict[str, Any]) -> List[str]:
        """Generate recommendations from predictions"""
        recommendations = []
        
        pred_list = predictions['predictions']
        if pred_list:
            avg_detections = np.mean([p['predicted_detections'] for p in pred_list])
            
            if avg_detections > 10:
                recommendations.append("آماده‌سازی تیم‌های عملیاتی برای افزایش فعالیت")
            
            if avg_detections < 5:
                recommendations.append("کاهش منابع نظارتی و تخصیص به مناطق دیگر")
        
        return recommendations
    
    def _generate_clustering_recommendations(self, clusters: Dict[str, Any]) -> List[str]:
        """Generate recommendations from clustering"""
        recommendations = []
        
        n_clusters = clusters['n_clusters']
        noise_points = clusters['noise_points']
        
        if n_clusters > 1:
            recommendations.append("تطبیق استراتژی‌های تشخیص با انواع مختلف دستگاه‌ها")
        
        if noise_points > 0:
            recommendations.append("بررسی دقیق دستگاه‌های غیرعادی")
        
        return recommendations
    
    def _generate_risk_recommendations(self, risk_scores: Dict[str, Any]) -> List[str]:
        """Generate recommendations from risk assessment"""
        recommendations = []
        
        areas = risk_scores['areas']
        if areas:
            critical_areas = [area for area in areas if area['risk_level'] == 'critical']
            
            if critical_areas:
                recommendations.append("تمرکز منابع بر مناطق بحرانی")
                recommendations.append("گشت‌زنی مکرر در مناطق پرخطر")
            
            recommendations.append("بروزرسانی مداوم ارزیابی ریسک")
        
        return recommendations
    
    async def _create_network_visualizations(self, df: pd.DataFrame, patterns: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations for network analysis"""
        visualizations = {}
        
        # Power consumption distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['power_consumption'], bins=20, alpha=0.7, color='blue')
        plt.title('توزیع مصرف برق')
        plt.xlabel('مصرف برق (وات)')
        plt.ylabel('تعداد دستگاه‌ها')
        plt.grid(True, alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        visualizations['power_distribution'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return visualizations
    
    async def _create_anomaly_visualizations(self, df: pd.DataFrame, anomalies: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations for anomaly detection"""
        visualizations = {}
        
        # Anomaly scores plot
        plt.figure(figsize=(12, 6))
        anomaly_scores = anomalies['anomaly_scores']
        plt.plot(anomaly_scores, 'b-', alpha=0.7, label='امتیاز ناهنجاری')
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='آستانه ناهنجاری')
        plt.title('امتیازات ناهنجاری در طول زمان')
        plt.xlabel('نمونه')
        plt.ylabel('امتیاز ناهنجاری')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        visualizations['anomaly_scores'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return visualizations
    
    async def _create_prediction_visualizations(self, df: pd.DataFrame, predictions: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations for predictions"""
        visualizations = {}
        
        # Historical vs predicted
        plt.figure(figsize=(12, 6))
        
        # Historical data
        dates = pd.to_datetime(df.index)
        plt.plot(dates, df['daily_detections'], 'b-', label='داده‌های تاریخی', alpha=0.7)
        
        # Predictions
        pred_list = predictions['predictions']
        if pred_list:
            pred_dates = [pd.to_datetime(p['date']) for p in pred_list]
            pred_values = [p['predicted_detections'] for p in pred_list]
            plt.plot(pred_dates, pred_values, 'r--', label='پیش‌بینی', linewidth=2)
        
        plt.title('پیش‌بینی تشخیص‌های روزانه')
        plt.xlabel('تاریخ')
        plt.ylabel('تعداد تشخیص‌ها')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        visualizations['predictions'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return visualizations
    
    async def _create_clustering_visualizations(self, df: pd.DataFrame, clusters: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations for clustering"""
        visualizations = {}
        
        # PCA for visualization
        features = self._prepare_clustering_features(df)
        pca_features = self.scalers['pca'].fit_transform(features)
        
        plt.figure(figsize=(10, 8))
        cluster_labels = clusters['cluster_labels']
        
        # Plot clusters
        for i in range(max(cluster_labels) + 1):
            mask = np.array(cluster_labels) == i
            plt.scatter(pca_features[mask, 0], pca_features[mask, 1], 
                       label=f'خوشه {i}', alpha=0.7)
        
        # Plot noise points
        noise_mask = np.array(cluster_labels) == -1
        if np.any(noise_mask):
            plt.scatter(pca_features[noise_mask, 0], pca_features[noise_mask, 1], 
                       c='red', marker='x', s=100, label='نویز', alpha=0.8)
        
        plt.title('خوشه‌بندی دستگاه‌ها')
        plt.xlabel('مولفه اصلی 1')
        plt.ylabel('مولفه اصلی 2')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        visualizations['clusters'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return visualizations
    
    async def _create_risk_visualizations(self, df: pd.DataFrame, risk_scores: Dict[str, Any]) -> Dict[str, str]:
        """Create visualizations for risk assessment"""
        visualizations = {}
        
        # Risk scores by area
        areas = risk_scores['areas']
        if areas:
            cities = [area['city'] for area in areas]
            scores = [area['risk_score'] for area in areas]
            
            plt.figure(figsize=(12, 8))
            bars = plt.bar(range(len(cities)), scores, alpha=0.7)
            
            # Color bars by risk level
            for i, area in enumerate(areas):
                if area['risk_level'] == 'critical':
                    bars[i].set_color('red')
                elif area['risk_level'] == 'high':
                    bars[i].set_color('orange')
                elif area['risk_level'] == 'medium':
                    bars[i].set_color('yellow')
                else:
                    bars[i].set_color('green')
            
            plt.title('امتیازات ریسک بر اساس منطقه')
            plt.xlabel('منطقه')
            plt.ylabel('امتیاز ریسک')
            plt.xticks(range(len(cities)), cities, rotation=45)
            plt.grid(True, alpha=0.3)
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            visualizations['risk_scores'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        return visualizations
    
    def _create_empty_result(self, analysis_type: AnalysisType) -> AnalysisResult:
        """Create empty result when no data is available"""
        return AnalysisResult(
            id=f"{analysis_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=analysis_type,
            timestamp=datetime.now(),
            data={},
            confidence=0.0,
            insights=["داده‌ای برای تحلیل موجود نیست"],
            recommendations=["جمع‌آوری داده‌های بیشتر"],
            visualizations={}
        )
    
    async def save_models(self):
        """Save trained models"""
        for name, model in self.models.items():
            model_path = self.models_dir / f"{name}.joblib"
            joblib.dump(model, model_path)
        
        for name, scaler in self.scalers.items():
            scaler_path = self.models_dir / f"{name}_scaler.joblib"
            joblib.dump(scaler, scaler_path)
        
        logger.info("Models saved successfully")
    
    async def load_models(self):
        """Load trained models"""
        for name in self.models.keys():
            model_path = self.models_dir / f"{name}.joblib"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)
        
        for name in self.scalers.keys():
            scaler_path = self.models_dir / f"{name}_scaler.joblib"
            if scaler_path.exists():
                self.scalers[name] = joblib.load(scaler_path)
        
        logger.info("Models loaded successfully")

# Global instance
ai_analytics = AIAnalyticsSystem()

# Convenience functions
async def analyze_network_patterns() -> AnalysisResult:
    """Analyze network patterns"""
    return await ai_analytics.analyze_network_patterns()

async def detect_anomalies() -> AnalysisResult:
    """Detect anomalies"""
    return await ai_analytics.detect_anomalies()

async def predict_future_activities(days_ahead: int = 7) -> AnalysisResult:
    """Predict future activities"""
    return await ai_analytics.predict_future_activities(days_ahead)

async def cluster_devices() -> AnalysisResult:
    """Cluster devices"""
    return await ai_analytics.cluster_devices()

async def assess_risk_levels() -> AnalysisResult:
    """Assess risk levels"""
    return await ai_analytics.assess_risk_levels()

if __name__ == "__main__":
    # Test the AI analytics system
    async def test():
        # Test network pattern analysis
        network_result = await analyze_network_patterns()
        print("Network analysis completed:", len(network_result.insights), "insights")
        
        # Test anomaly detection
        anomaly_result = await detect_anomalies()
        print("Anomaly detection completed:", anomaly_result.data.get('anomaly_count', 0), "anomalies")
        
        # Test risk assessment
        risk_result = await assess_risk_levels()
        print("Risk assessment completed:", len(risk_result.data.get('areas', [])), "areas")
    
    asyncio.run(test())