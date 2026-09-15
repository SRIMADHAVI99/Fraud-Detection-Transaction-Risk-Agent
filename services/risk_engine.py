import numpy as np
from ml.fraud_detector import FraudDetector
from ml.anomaly_detector import AnomalyDetector
from ml.explainability import generate_explanations
from config import Config

class RiskEngine:
    def __init__(self):
        self.fraud_detector = FraudDetector()
        self.anomaly_detector = AnomalyDetector()

    def evaluate_transaction(self, raw_data: dict) -> dict:
        """
        Evaluates transaction using ML models, anomaly detection, and risk signal fusion.
        Returns comprehensive risk analysis object.
        """
        # 1. Supervised Fraud Prediction Probability
        fraud_prob = self.fraud_detector.predict_probability(raw_data)
        
        # 2. Unsupervised Anomaly Detection
        anomaly_res = self.anomaly_detector.detect_anomaly(raw_data)
        is_anomaly = anomaly_res['is_anomaly']
        
        # 3. Dynamic Signal Fusion
        ml_base_score = fraud_prob * 100.0
        
        # Add risk boosters for strong risk signals
        boost = 0.0
        if is_anomaly:
            boost += 15.0
            
        amt = float(raw_data.get('amount', 0.0))
        avg_amt = float(raw_data.get('avg_amount', 2500.0)) or 2500.0
        ratio = amt / avg_amt
        
        new_dev = raw_data.get('new_device') in [True, 1, '1', 'Yes', 'yes', 'true']
        loc_chg = raw_data.get('location_change') in [True, 1, '1', 'Yes', 'yes', 'true']
        txns_10m = int(raw_data.get('transactions_last_10min', 1))
        hour = int(raw_data.get('hour', 12))
        is_night = (hour < 6 or hour >= 23)
        
        if new_dev and loc_chg:
            boost += 15.0
        elif new_dev or loc_chg:
            boost += 8.0
            
        if txns_10m >= 5:
            boost += 20.0
        elif txns_10m >= 3:
            boost += 10.0
            
        if ratio >= 5.0:
            boost += 20.0
        elif ratio >= 3.0:
            boost += 10.0
            
        if is_night and ratio >= 3.0:
            boost += 12.0

        # Weighted combination: 65% ML model + 35% Risk Signals & Anomaly Boost
        combined_score = (0.65 * ml_base_score) + (0.35 * min(ml_base_score + boost, 100.0))
        risk_score = min(max(round(combined_score, 1), 0.0), 99.9)

        # Determine user-facing Risk Level
        if risk_score <= Config.RISK_THRESHOLD_SAFE:
            risk_level = 'SAFE'
        elif risk_score <= Config.RISK_THRESHOLD_CHECK:
            risk_level = 'CHECK'
        else:
            risk_level = 'HIGH RISK'
            
        # Generate user-facing reasons
        explanation = generate_explanations(raw_data, fraud_prob, is_anomaly)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'fraud_probability': round(fraud_prob, 4),
            'is_anomaly': is_anomaly,
            'reasons': explanation['user_reasons'],
            'technical_details': explanation['technical_details']
        }
