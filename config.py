import os
import shutil
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def _get_database_uri():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        return db_url

    is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))
    source_db = BASE_DIR / 'database' / 'fraudguard.db'

    if is_serverless:
        tmp_dir = Path(tempfile.gettempdir())
        tmp_db = tmp_dir / 'fraudguard.db'
        if not tmp_db.exists() and source_db.exists():
            try:
                shutil.copy2(source_db, tmp_db)
            except Exception as e:
                print(f"Warning: Could not copy database to {tmp_db}: {e}")
        return f"sqlite:///{tmp_db.as_posix()}"
    else:
        return f"sqlite:///{source_db.as_posix()}"

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fraudguard-default-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
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
