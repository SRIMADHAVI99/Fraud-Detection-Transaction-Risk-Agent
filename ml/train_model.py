import sys
import os
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)

# Adjust path import
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from ml.preprocessing import extract_features, FEATURE_COLUMNS
from generate_data import generate_transactions

def train_and_evaluate():
    data_path = BASE_DIR / 'data' / 'transactions.csv'
    model_dir = BASE_DIR / 'models'
    model_dir.mkdir(exist_ok=True)
    
    if not data_path.exists():
        print("Dataset not found. Generating 15,000 synthetic transactions...")
        generate_transactions(num_records=15000)
        
    print(f"Loading dataset from {data_path}...")
    df = pd.read_csv(data_path)
    
    X = extract_features(df)
    y = df['is_fraud'].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Dataset split: {len(X_train)} train, {len(X_test)} test records.")
    
    # Standard Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 1. Supervised Random Forest Model with class balancing
    print("Training Random Forest Classifier (Supervised Fraud Model)...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train_scaled, y_train)
    
    # Predict probabilities and labels
    y_proba = clf.predict_proba(X_test_scaled)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)
    
    # Calculate Evaluation Metrics
    precision = float(precision_score(y_test, y_pred))
    recall = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    pr_auc = float(average_precision_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    # Feature importances
    importances = dict(zip(FEATURE_COLUMNS, [float(v) for v in clf.feature_importances_]))
    
    # 2. Unsupervised Isolation Forest Model (Anomaly Detection)
    print("Training Isolation Forest (Unsupervised Anomaly Model)...")
    iso = IsolationForest(
        n_estimators=100,
        contamination=0.10,
        random_state=42,
        n_jobs=-1
    )
    # Fit Isolation Forest on normal training data or all training data
    iso.fit(X_train_scaled)
    
    # Save artifacts
    fraud_model_path = model_dir / 'fraud_model.pkl'
    anomaly_model_path = model_dir / 'anomaly_model.pkl'
    scaler_path = model_dir / 'scaler.pkl'
    metadata_path = model_dir / 'model_metadata.json'
    
    joblib.dump(clf, fraud_model_path)
    joblib.dump(iso, anomaly_model_path)
    joblib.dump(scaler, scaler_path)
    
    metadata = {
        'model_name': 'RandomForestClassifier + IsolationForest',
        'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_samples': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_columns': FEATURE_COLUMNS,
        'metrics': {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4),
            'roc_auc': round(roc_auc, 4),
            'pr_auc': round(pr_auc, 4), # PR-AUC metric
            'confusion_matrix': cm
        },
        'feature_importances': importances,
        'hyperparameters': {
            'n_estimators': 100,
            'max_depth': 10,
            'class_weight': 'balanced',
            'isolation_forest_contamination': 0.10
        }
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("\n================ MODEL TRAINING & EVALUATION REPORT ================")
    print(f" Model Trained : RandomForestClassifier (balanced)")
    print(f" Precision     : {precision:.4f}")
    print(f" Recall        : {recall:.4f}")
    print(f" F1-Score      : {f1:.4f}")
    print(f" ROC-AUC       : {roc_auc:.4f}")
    print(f" PR-AUC        : {pr_auc:.4f}")
    print(f" Confusion Matrix:\n   TN: {cm[0][0]}  FP: {cm[0][1]}\n   FN: {cm[1][0]}  TP: {cm[1][1]}")
    print(f" Artifacts saved to: {model_dir}")
    print("===================================================================\n")

if __name__ == '__main__':
    train_and_evaluate()
