import json
import time
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import threading
from datetime import datetime
import os

class AnomalyDetector:
    def __init__(self, contamination=0.05, random_state=42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.telemetry_file = "../telemetry.jsonl"
        self.anomalies_file = "../anomalies.json"
        self.last_position = 0
        self.training_data = []
        self.anomalies = []
        self.incorrect_anomalies = 0
        
    def load_telemetry_data(self):
        """Load new telemetry data from the JSONL file"""
        data = []
        try:
            with open(self.telemetry_file, 'r') as f:
                lines = f.readlines()
                for line in lines[self.last_position:]:
                    if line.strip():
                        data.append(json.loads(line))
            self.last_position = len(lines)
        except FileNotFoundError:
            print(f"Telemetry file {self.telemetry_file} not found. Waiting for data...")
        return data
    
    def extract_features(self, data_point):
        """Extract features from a telemetry data point"""
        return [
            data_point['altitude'],
            data_point['airspeed'],
            data_point['pitch'],
            data_point['vibration']
        ]
    
    def train_model(self, training_data):
        """Train the isolation forest model"""
        if len(training_data) < 120:
            print("Not enough training data. Need at least 120 data points.")
            return False
            
        features = np.array([self.extract_features(point) for point in training_data])
        features_scaled = self.scaler.fit_transform(features)
        
        self.model.fit(features_scaled)
        self.is_trained = True
        print(f"Model trained with {len(training_data)} data points")
        return True
    
    def detect_anomalies(self, data_points):
        """Detect anomalies in the given data points"""
        if not self.is_trained:
            print("Model not trained yet. Skipping anomaly detection.")
            return []
            
        features = np.array([self.extract_features(point) for point in data_points])
        features_scaled = self.scaler.transform(features)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.model.predict(features_scaled)
        
        anomalies = []
        for i, (point, pred) in enumerate(zip(data_points, predictions)):
            if pred == -1:  # Anomaly detected
                anomaly = {
                    'timestamp': point['timestamp'],
                    'altitude': point['altitude'],
                    'airspeed': point['airspeed'],
                    'pitch': point['pitch'],
                    'vibration': point['vibration'],
                    'engineFailure': point['engineFailure'],
                    'detected_at': datetime.now().isoformat(),
                    'severity': self.calculate_severity(point)
                }
                if not anomaly['engineFailure']:
                  print(f"Vibration={point['vibration']:.2f}g, Altitude={point['altitude']:.0f}ft, Speed={point['airspeed']:.0f}kts, Pitch={point['pitch']:.2f} was NOT an ANOMALY!")
                  self.training_data.append(point)
                  self.incorrect_anomalies += 1
                  if self.incorrect_anomalies > 10:
                    print("Retraining model...")
                    self.train_model(self.training_data)
                    self.incorrect_anomalies = 0
                  continue
                anomalies.append(anomaly)
                print(f"🚨 ANOMALY DETECTED: Vibration={point['vibration']:.2f}g, "
                      f"Altitude={point['altitude']:.0f}ft, Speed={point['airspeed']:.0f}kts")
        
        return anomalies
    
    def calculate_severity(self, data_point):
        """Calculate anomaly severity based on vibration levels"""
        vibration = data_point['vibration']
        if vibration > 8.0:
            return 'CRITICAL'
        elif vibration > 6.0:
            return 'HIGH'
        elif vibration > 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def save_anomalies(self, new_anomalies):
        """Save detected anomalies to JSON file"""
        # Load existing anomalies
        existing_anomalies = []
        try:
            with open(self.anomalies_file, 'r') as f:
                existing_anomalies = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Add new anomalies
        all_anomalies = existing_anomalies + new_anomalies
        
        # Save to file
        with open(self.anomalies_file, 'w') as f:
            json.dump(all_anomalies, f, indent=2)
        
        print(f"Saved {len(new_anomalies)} new anomalies to {self.anomalies_file}")

    def clean_anomalies(self):
        """Clean anomalies from the anomalies file"""
        open(self.anomalies_file, 'w').close()
    
    def run_detection_loop(self):
        """Main detection loop"""
        self.clean_anomalies()
        print("Starting anomaly detection engine...")
        
        while True:
            try:
                # Load new telemetry data
                new_data = self.load_telemetry_data()
                if new_data:
                    # Separate training and testing data
                    training_data = [d for d in new_data if d.get('trainingPhase', True)]
                    testing_data = [d for d in new_data if not d.get('trainingPhase', True)]
                    # Train model with training data
                    if training_data and not self.is_trained:
                        self.training_data.extend(training_data)
                        self.train_model(self.training_data)
                    
                    # Detect anomalies in testing data
                    if testing_data and self.is_trained:
                        print(f"Detecting anomalies in {len(testing_data)} data points")
                        anomalies = self.detect_anomalies(testing_data)
                        print(f"Detected {len(anomalies)} anomalies")
                        if anomalies:
                            self.save_anomalies(anomalies)
                else: print("Didn't found any new data. Waiting for data...")
                
                # Wait before next check
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\nStopping anomaly detection engine...")
                break
            except Exception as e:
                print(f"Error in detection loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    detector = AnomalyDetector()
    detector.run_detection_loop()