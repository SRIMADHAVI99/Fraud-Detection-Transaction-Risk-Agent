import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(64), nullable=False)
    device = db.Column(db.String(64), nullable=False)
    payment_method = db.Column(db.String(32), nullable=False)
    hour = db.Column(db.Integer, nullable=False, default=12)
    avg_amount = db.Column(db.Float, nullable=False, default=2500.0)
    amount_ratio = db.Column(db.Float, nullable=False, default=1.0)
    new_device = db.Column(db.Boolean, nullable=False, default=False)
    location_change = db.Column(db.Boolean, nullable=False, default=False)
    transactions_last_10min = db.Column(db.Integer, nullable=False, default=1)
    
    risk_score = db.Column(db.Float, nullable=False, default=0.0)
    risk_level = db.Column(db.String(20), nullable=False, default='SAFE')
    fraud_probability = db.Column(db.Float, nullable=False, default=0.0)
    is_anomaly = db.Column(db.Boolean, nullable=False, default=False)
    reasons = db.Column(db.Text, nullable=True) # Serialized JSON array of strings
    status = db.Column(db.String(20), nullable=False, default='ALLOWED') # ALLOWED, UNDER_REVIEW, BLOCKED
    
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        reasons_list = []
        if self.reasons:
            try:
                reasons_list = json.loads(self.reasons)
            except Exception:
                reasons_list = [r.strip() for r in self.reasons.split(';') if r.strip()]
                
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'amount': round(self.amount, 2),
            'location': self.location,
            'device': self.device,
            'payment_method': self.payment_method,
            'hour': self.hour,
            'avg_amount': round(self.avg_amount, 2),
            'amount_ratio': round(self.amount_ratio, 2),
            'new_device': self.new_device,
            'location_change': self.location_change,
            'transactions_last_10min': self.transactions_last_10min,
            'risk_score': round(self.risk_score, 1),
            'risk_level': self.risk_level,
            'fraud_probability': round(self.fraud_probability * 100, 1),
            'is_anomaly': self.is_anomaly,
            'reasons': reasons_list,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class FraudAlert(db.Model):
    __tablename__ = 'fraud_alerts'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(32), db.ForeignKey('transactions.transaction_id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False, default='HIGH')
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Action(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(32), db.ForeignKey('transactions.transaction_id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False) # ALLOW, REVIEW, BLOCK
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'action_type': self.action_type,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
