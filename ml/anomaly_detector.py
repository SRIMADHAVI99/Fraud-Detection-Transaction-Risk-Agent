import joblib
import pandas as pd
from pathlib import Path
from ml.preprocessing import prepare_feature_dict, FEATURE_COLUMNS

class AnomalyDetector:
    def __init__(self, model_path=None, scaler_path=None):
        base_dir = Path(__file__).resolve().parent.parent
        self.model_path = model_path or (base_dir / 'models' / 'anomaly_model.pkl')
        self.scaler_path = scaler_path or (base_dir / 'models' / 'scaler.pkl')
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        if self.model_path.exists() and self.scaler_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            except Exception as e:
                print(f"Warning: Could not load Anomaly Model ({e})")
                self.model = None
                self.scaler = None
        else:
            print(f"Warning: Anomaly Model file {self.model_path} not found.")

    def detect_anomaly(self, raw_data: dict) -> dict:
        """Determines if transaction pattern is unusual using Isolation Forest."""
        if self.model is None or self.scaler is None:
            return self._heuristic_fallback(raw_data)
            
        feat_dict = prepare_feature_dict(raw_data)
        df_feat = pd.DataFrame([feat_dict])[FEATURE_COLUMNS]
        scaled = self.scaler.transform(df_feat)
        
        pred = self.model.predict(scaled)[0] # -1 for outlier/anomaly, 1 for inlier
        raw_score = float(self.model.score_samples(scaled)[0])
        
        is_anomaly = bool(pred == -1)
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(raw_score, 4)
        }

    def _heuristic_fallback(self, data: dict) -> dict:
        amt = float(data.get('amount', 0))
        avg = float(data.get('avg_amount', 2500)) or 2500.0
        ratio = amt / avg
        txns = int(data.get('transactions_last_10min', 1))
        new_dev = 1 if data.get('new_device') in [True, 1, '1', 'Yes', 'yes'] else 0
        loc_chg = 1 if data.get('location_change') in [True, 1, '1', 'Yes', 'yes'] else 0
        
        # Rule of thumb for fallback
        is_anomaly = (ratio > 4.5) or (txns >= 5) or (new_dev and loc_chg and ratio > 2.5)
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': -0.65 if is_anomaly else 0.15
        }
