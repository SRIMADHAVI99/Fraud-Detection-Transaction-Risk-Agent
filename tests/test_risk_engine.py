import pytest
from services.risk_engine import RiskEngine

@pytest.fixture
def risk_engine():
    return RiskEngine()

def test_safe_transaction(risk_engine):
    safe_data = {
        'amount': 2500,
        'location': 'Hyderabad',
        'device': 'Known Device',
        'payment_method': 'UPI',
        'hour': 14,
        'avg_amount': 2500,
        'new_device': False,
        'location_change': False,
        'transactions_last_10min': 1
    }
    res = risk_engine.evaluate_transaction(safe_data)
    assert res['risk_level'] == 'SAFE'
    assert res['risk_score'] <= 30.0
    assert len(res['reasons']) > 0

def test_suspicious_transaction(risk_engine):
    suspicious_data = {
        'amount': 25000,
        'location': 'Mumbai',
        'device': 'New Phone',
        'payment_method': 'Credit Card',
        'hour': 23,
        'avg_amount': 2500,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 4
    }
    res = risk_engine.evaluate_transaction(suspicious_data)
    assert res['risk_level'] in ['CHECK', 'HIGH RISK']
    assert res['risk_score'] > 30.0

def test_high_risk_transaction(risk_engine):
    high_risk_data = {
        'amount': 85000,
        'location': 'Singapore',
        'device': 'Unknown Web Browser',
        'payment_method': 'Net Banking',
        'hour': 3,
        'avg_amount': 2500,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 8
    }
    res = risk_engine.evaluate_transaction(high_risk_data)
    assert res['risk_level'] == 'HIGH RISK'
    assert res['risk_score'] > 60.0
