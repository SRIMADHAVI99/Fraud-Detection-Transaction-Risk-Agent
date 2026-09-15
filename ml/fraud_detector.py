import joblib
import pandas as pd
from pathlib import Path
from ml.preprocessing import prepare_feature_dict, FEATURE_COLUMNS

class FraudDetector:
    def __init__(self, model_path=None, scaler_path=None):
        base_dir = Path(__file__).resolve().parent.parent
        self.model_path = model_path or (base_dir / 'models' / 'fraud_model.pkl')
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
                print(f"Warning: Could not load Fraud Model ({e})")
                self.model = None
                self.scaler = None
        else:
            print(f"Warning: Model file {self.model_path} not found.")

    def predict_probability(self, raw_data: dict) -> float:
        """Returns predicted fraud probability (0.0 to 1.0)."""
        if self.model is None or self.scaler is None:
            # Fallback heuristic if model files are missing
            return self._heuristic_fallback(raw_data)
            
        feat_dict = prepare_feature_dict(raw_data)
        df_feat = pd.DataFrame([feat_dict])[FEATURE_COLUMNS]
        scaled = self.scaler.transform(df_feat)
        
        proba = float(self.model.predict_proba(scaled)[0][1])
        return proba

    def _heuristic_fallback(self, data: dict) -> float:
        amt = float(data.get('amount', 0))
        avg = float(data.get('avg_amount', 2500)) or 2500.0
        ratio = amt / avg
        new_dev = 1 if data.get('new_device') in [True, 1, '1', 'Yes', 'yes'] else 0
        loc_chg = 1 if data.get('location_change') in [True, 1, '1', 'Yes', 'yes'] else 0
        txns = int(data.get('transactions_last_10min', 1))
        
        score = 0.05
        if ratio > 4.0: score += 0.35
        if new_dev: score += 0.25
        if loc_chg: score += 0.20
        if txns >= 4: score += 0.25
        return min(round(score, 4), 0.99)
