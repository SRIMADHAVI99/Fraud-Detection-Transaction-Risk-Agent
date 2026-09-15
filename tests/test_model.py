import pytest
import pandas as pd
from ml.preprocessing import extract_features, FEATURE_COLUMNS, prepare_feature_dict
from ml.fraud_detector import FraudDetector
from ml.anomaly_detector import AnomalyDetector

def test_feature_extraction():
    data = {
        'amount': [5000.0],
        'hour': [14],
        'avg_amount': [2500.0],
        'new_device': [1],
        'location_change': [0],
        'transactions_last_10min': [2]
    }
    df = pd.DataFrame(data)
    features = extract_features(df)
    
    assert list(features.columns) == FEATURE_COLUMNS
    assert len(features) == 1
    assert features.iloc[0]['amount_ratio'] == 2.0
    assert features.iloc[0]['is_night_time'] == 0
    assert features.iloc[0]['high_velocity'] == 0

def test_prepare_feature_dict():
    raw = {
        'amount': '85000',
        'hour': '3',
        'avg_amount': '2500',
        'new_device': 'Yes',
        'location_change': True,
        'transactions_last_10min': 6
    }
    feat = prepare_feature_dict(raw)
    assert feat['amount'] == 85000.0
    assert feat['amount_ratio'] == 34.0
    assert feat['new_device'] == 1
    assert feat['location_change'] == 1
    assert feat['is_night_time'] == 1
    assert feat['high_velocity'] == 1

def test_fraud_detector_inference():
    detector = FraudDetector()
    sample = {
        'amount': 2500.0,
        'hour': 14,
        'avg_amount': 2500.0,
        'new_device': False,
        'location_change': False,
        'transactions_last_10min': 1
    }
    proba = detector.predict_probability(sample)
    assert isinstance(proba, float)
    assert 0.0 <= proba <= 1.0

def test_anomaly_detector_inference():
    detector = AnomalyDetector()
    sample = {
        'amount': 85000.0,
        'hour': 3,
        'avg_amount': 2500.0,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 6
    }
    res = detector.detect_anomaly(sample)
    assert 'is_anomaly' in res
    assert isinstance(res['is_anomaly'], bool)
    assert 'anomaly_score' in res
