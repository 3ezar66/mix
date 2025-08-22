import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class MinerClassifier:
    def __init__(self, model_path: str = 'models/miner_classifier.joblib'):
        self.model_path = model_path
        self.model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.logger = logging.getLogger('MinerClassifier')
        self.feature_columns = [
            'cpu_usage',
            'gpu_usage',
            'memory_usage',
            'network_upload',
            'network_download',
            'connection_count',
            'mining_port_count',
            'known_pool_connections',
            'process_signature_match',
            'gpu_temp',
            'cpu_temp'
        ]

    def prepare_features(self, raw_data: Dict) -> np.ndarray:
        """Convert raw device metrics into ML features"""
        features = [
            raw_data.get('cpu_usage', 0),
            raw_data.get('gpu_usage', 0),
            raw_data.get('memory_usage', 0),
            raw_data.get('network_stats', {}).get('upload_rate', 0),
            raw_data.get('network_stats', {}).get('download_rate', 0),
            len(raw_data.get('connections', [])),
            self._count_mining_ports(raw_data.get('connections', [])),
            self._count_pool_connections(raw_data.get('connections', [])),
            self._check_process_signatures(raw_data.get('processes', [])),
            raw_data.get('gpu_temp', 0),
            raw_data.get('cpu_temp', 0)
        ]
        return np.array(features).reshape(1, -1)

    def _count_mining_ports(self, connections: List[Dict]) -> int:
        """Count connections to common mining ports"""
        mining_ports = {3333, 4444, 5555, 7777, 8888, 9999, 14444, 14433}
        return sum(1 for conn in connections if conn.get('port') in mining_ports)

    def _count_pool_connections(self, connections: List[Dict]) -> int:
        """Count connections to known mining pools"""
        pool_keywords = {'pool', 'mine', 'crypto', 'eth', 'btc', 'xmr'}
        return sum(1 for conn in connections 
                  if any(kw in conn.get('destination', '').lower() for kw in pool_keywords))

    def _check_process_signatures(self, processes: List[Dict]) -> int:
        """Check for known mining process signatures"""
        mining_keywords = {
            'xmrig', 'ethminer', 'cgminer', 'bfgminer', 'ccminer',
            'phoenixminer', 'nbminer', 'teamredminer', 'gminer', 't-rex'
        }
        return sum(1 for proc in processes 
                  if any(kw in proc.get('name', '').lower() for kw in mining_keywords))

    def train(self, training_data: pd.DataFrame) -> None:
        """Train the classifier on labeled data"""
        try:
            X = training_data[self.feature_columns]
            y = training_data['is_mining']

            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred)
            }

            self.logger.info(f'Model training completed with metrics: {metrics}')

            # Save model
            self.save_model()

        except Exception as e:
            self.logger.error(f'Error during model training: {str(e)}')
            raise

    def predict(self, device_metrics: Dict) -> Tuple[bool, float]:
        """Predict whether a device is mining based on its metrics"""
        try:
            if self.model is None:
                self.load_model()

            # Prepare features
            features = self.prepare_features(device_metrics)
            
            # Scale features
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features

            # Get prediction and probability
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0][1]

            # Log prediction details
            self.logger.info(f'Prediction made for device with confidence {probability:.2f}')

            return bool(prediction), float(probability)

        except Exception as e:
            self.logger.error(f'Error during prediction: {str(e)}')
            raise

    def save_model(self) -> None:
        """Save the trained model and scaler"""
        if self.model is not None and self.scaler is not None:
            try:
                model_data = {
                    'model': self.model,
                    'scaler': self.scaler,
                    'feature_columns': self.feature_columns,
                    'timestamp': datetime.now().isoformat()
                }
                joblib.dump(model_data, self.model_path)
                self.logger.info(f'Model saved successfully to {self.model_path}')
            except Exception as e:
                self.logger.error(f'Error saving model: {str(e)}')
                raise

    def load_model(self) -> None:
        """Load a trained model and scaler"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.logger.info(
                f'Model loaded successfully from {self.model_path} '
                f'(trained on {model_data["timestamp"]})'
            )
        except Exception as e:
            self.logger.error(f'Error loading model: {str(e)}')
            raise

    def update_model(self, new_data: pd.DataFrame) -> None:
        """Update the model with new training data"""
        try:
            # Combine new data with existing training data if available
            if self.model is not None:
                # Extract feature importance from current model
                feature_importance = pd.DataFrame({
                    'feature': self.feature_columns,
                    'importance': self.model.feature_importances_
                })
                self.logger.info(f'Current feature importance:\n{feature_importance}')

            # Train model with new data
            self.train(new_data)

            self.logger.info('Model updated successfully')

        except Exception as e:
            self.logger.error(f'Error updating model: {str(e)}')
            raise

    def get_feature_importance(self) -> pd.DataFrame:
        """Get the importance of each feature in the model"""
        if self.model is None:
            raise ValueError('Model not trained or loaded')

        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        })
        return importance.sort_values('importance', ascending=False)

    def evaluate_prediction(self, device_metrics: Dict, actual_mining: bool) -> Dict:
        """Evaluate a single prediction against known ground truth"""
        prediction, confidence = self.predict(device_metrics)
        
        evaluation = {
            'predicted': prediction,
            'actual': actual_mining,
            'confidence': confidence,
            'correct': prediction == actual_mining,
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f'Prediction evaluation: {evaluation}')
        return evaluation