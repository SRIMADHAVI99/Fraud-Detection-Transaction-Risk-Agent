import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fraudguard-default-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{BASE_DIR / 'database' / 'fraudguard.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DATA_DIR = BASE_DIR / 'data'
    MODEL_DIR = BASE_DIR / 'models'
    DATABASE_DIR = BASE_DIR / 'database'
    
    FRAUD_MODEL_PATH = MODEL_DIR / 'fraud_model.pkl'
    ANOMALY_MODEL_PATH = MODEL_DIR / 'anomaly_model.pkl'
    SCALER_PATH = MODEL_DIR / 'scaler.pkl'
    METADATA_PATH = MODEL_DIR / 'model_metadata.json'
    
    DATASET_PATH = DATA_DIR / 'transactions.csv'
    SAMPLE_DATASET_PATH = DATA_DIR / 'sample_transactions.csv'

    # Risk thresholds
    RISK_THRESHOLD_SAFE = 30
    RISK_THRESHOLD_CHECK = 60
