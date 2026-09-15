import pytest
from app import create_app
from database.schema import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_stats_api(client):
    res = client.get('/api/stats')
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert 'total_transactions' in json_data['data']

def test_post_check_api(client):
    payload = {
        'amount': 5000,
        'location': 'Bangalore',
        'device': 'Chrome',
        'payment_method': 'UPI',
        'avg_amount': 2500,
        'new_device': False,
        'location_change': False,
        'transactions_last_10min': 1
    }
    res = client.post('/api/check', json=payload)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert 'transaction' in json_data['data']
    assert 'risk' in json_data['data']
    assert json_data['data']['risk']['risk_level'] in ['SAFE', 'CHECK', 'HIGH RISK']

def test_update_action_api(client):
    # First create a transaction via check
    payload = {
        'amount': 95000,
        'location': 'Dubai',
        'device': 'Unknown Client',
        'payment_method': 'Credit Card',
        'avg_amount': 2500,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 6
    }
    check_res = client.post('/api/check', json=payload).get_json()
    txn_id = check_res['data']['transaction']['transaction_id']

    # Update action to BLOCK
    action_res = client.post(f'/api/transactions/{txn_id}/action', json={'action': 'BLOCK'})
    assert action_res.status_code == 200
    assert action_res.get_json()['data']['status'] == 'BLOCKED'

def test_reports_summary_api(client):
    res = client.get('/api/reports')
    assert res.status_code == 200
    assert res.get_json()['success'] is True

def test_ai_investigate_api(client):
    payload = {
        'amount': 50000,
        'location': 'Mumbai',
        'device': 'New Phone',
        'payment_method': 'Net Banking',
        'query': 'Why was this payment flagged?'
    }
    res = client.post('/api/ai/investigate', json=payload)
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data['success'] is True
    assert 'answer' in json_data['data']

def test_settings_api(client):
    # GET settings
    get_res = client.get('/api/settings')
    assert get_res.status_code == 200
    assert get_res.get_json()['success'] is True

    # PUT settings
    put_res = client.put('/api/settings', json={
        'notifications_safety': 'OFF',
        'auto_block_threshold': '70'
    })
    assert put_res.status_code == 200
    assert put_res.get_json()['data']['auto_block_threshold'] == '70'

def test_pdf_report_download_api(client):
    res = client.get('/api/reports/download')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'

