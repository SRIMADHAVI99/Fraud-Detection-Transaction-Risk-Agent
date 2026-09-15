import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    'amount',
    'hour',
    'avg_amount',
    'amount_ratio',
    'new_device',
    'location_change',
    'transactions_last_10min',
    'is_night_time',
    'high_velocity'
]

def prepare_feature_dict(data: dict) -> dict:
    """Prepares and validates feature dictionary from single input data."""
    amount = float(data.get('amount', 0.0))
    avg_amount = float(data.get('avg_amount', 2500.0))
    if avg_amount <= 0:
        avg_amount = 2500.0
        
    amount_ratio = amount / avg_amount
    hour = int(data.get('hour', 12))
    new_device = 1 if data.get('new_device') in [True, 1, '1', 'Yes', 'yes', 'true'] else 0
    location_change = 1 if data.get('location_change') in [True, 1, '1', 'Yes', 'yes', 'true'] else 0
    txns_10m = int(data.get('transactions_last_10min', 1))
    
    is_night_time = 1 if (hour < 6 or hour >= 23) else 0
    high_velocity = 1 if txns_10m >= 3 else 0
    
    return {
        'amount': amount,
        'hour': hour,
        'avg_amount': avg_amount,
        'amount_ratio': amount_ratio,
        'new_device': new_device,
        'location_change': location_change,
        'transactions_last_10min': txns_10m,
        'is_night_time': is_night_time,
        'high_velocity': high_velocity
    }

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts ML features DataFrame from raw transaction records."""
    df_feat = df.copy()
    
    # Fill defaults if missing
    if 'avg_amount' not in df_feat.columns or df_feat['avg_amount'].isnull().any():
        df_feat['avg_amount'] = 2500.0
    df_feat['avg_amount'] = df_feat['avg_amount'].replace(0, 2500.0)
    
    if 'amount_ratio' not in df_feat.columns:
        df_feat['amount_ratio'] = df_feat['amount'] / df_feat['avg_amount']
        
    if 'hour' not in df_feat.columns:
        df_feat['hour'] = 12
        
    if 'new_device' in df_feat.columns:
        df_feat['new_device'] = df_feat['new_device'].astype(int)
    else:
        df_feat['new_device'] = 0
        
    if 'location_change' in df_feat.columns:
        df_feat['location_change'] = df_feat['location_change'].astype(int)
    else:
        df_feat['location_change'] = 0
        
    if 'transactions_last_10min' not in df_feat.columns:
        df_feat['transactions_last_10min'] = 1
        
    df_feat['is_night_time'] = ((df_feat['hour'] < 6) | (df_feat['hour'] >= 23)).astype(int)
    df_feat['high_velocity'] = (df_feat['transactions_last_10min'] >= 3).astype(int)
    
    return df_feat[FEATURE_COLUMNS]
