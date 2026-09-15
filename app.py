import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_cors import CORS

from config import Config
from database.schema import db, Transaction, FraudAlert, Setting
from routes.dashboard import dashboard_bp
from routes.transactions import transactions_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.checker import checker_bp
from ml.train_model import train_and_evaluate

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)

    # Register API Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(checker_bp)

    # Page Routes
    @app.route('/')
    def index():
        return render_template('index.html', page_title='Fraud Intelligence Overview')

    @app.route('/transactions')
    def transactions_page():
        return render_template('transactions.html', page_title='Transactions')

    @app.route('/suspicious')
    def suspicious_page():
        return render_template('suspicious.html', page_title='Threat Center')

    @app.route('/safety-check')
    def safety_check_page():
        return render_template('safety_check.html', page_title='Safety Check')

    @app.route('/ai-check')
    def ai_check_page():
        metadata = {}
        meta_path = Config.METADATA_PATH
        if meta_path.exists():
            try:
                with open(meta_path, 'r') as f:
                    metadata = json.load(f)
            except Exception:
                pass
        return render_template('ai_check.html', page_title='AI Fraud Investigator', metadata=metadata)

    @app.route('/activity')
    def activity_page():
        return render_template('activity.html', page_title='Risk Analytics')

    @app.route('/reports')
    def reports_page():
        return render_template('reports.html', page_title='Security Reports')

    @app.route('/settings')
    def settings_page():
        return render_template('settings.html', page_title='Settings')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('index.html', page_title='Fraud Intelligence Overview'), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    with app.app_context():
        db.create_all()
        _init_db_and_models()

    return app

def _init_db_and_models():
    """Ensure ML models exist and populate DB cleanly if empty."""
    if not Config.FRAUD_MODEL_PATH.exists() or not Config.ANOMALY_MODEL_PATH.exists():
        print("ML models missing. Training initial models...")
        train_and_evaluate()

    if Transaction.query.count() == 0:
        csv_path = Config.DATASET_PATH
        if not csv_path.exists():
            print("Dataset file missing. Generating data and training models...")
            train_and_evaluate()
            
        if csv_path.exists():
            print("Seeding database with transaction records...")
            df = pd.read_csv(csv_path)
            
            batch = []
            alerts = []
            
            for idx, row in df.iterrows():
                is_fraud = int(row.get('is_fraud', 0))
                new_dev = bool(row.get('new_device', 0))
                loc_chg = bool(row.get('location_change', 0))
                txns_10m = int(row.get('transactions_last_10min', 1))
                ratio = float(row.get('amount_ratio', 1.0))
                
                # Dynamic pre-calculated risk score bounds
                if is_fraud:
                    score = min(70.0 + (ratio * 3) + (txns_10m * 2), 99.9)
                    level = 'HIGH RISK'
                    status = 'BLOCKED'
                    reasons = ["High-risk behavioral pattern detected", "Unusual account activity"]
                elif ratio > 3.0 or new_dev or loc_chg or txns_10m >= 3:
                    score = min(35.0 + (ratio * 4), 60.0)
                    level = 'CHECK'
                    status = 'UNDER_REVIEW'
                    reasons = ["Unusual amount or parameter observed"]
                else:
                    score = max(5.0, round(ratio * 8.0, 1))
                    level = 'SAFE'
                    status = 'ALLOWED'
                    reasons = ["Regular purchasing behavior"]
                    
                created_dt = datetime.now()
                if 'created_at' in row and pd.notnull(row['created_at']):
                    try:
                        created_dt = datetime.strptime(str(row['created_at']), '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        pass

                txn = Transaction(
                    transaction_id=str(row['transaction_id']),
                    amount=float(row['amount']),
                    location=str(row['location']),
                    device=str(row['device']),
                    payment_method=str(row['payment_method']),
                    hour=int(row['hour']),
                    avg_amount=float(row['avg_amount']),
                    amount_ratio=float(row['amount_ratio']),
                    new_device=new_dev,
                    location_change=loc_chg,
                    transactions_last_10min=txns_10m,
                    risk_score=round(score, 1),
                    risk_level=level,
                    fraud_probability=round(score / 100.0, 4),
                    is_anomaly=bool(is_fraud or ratio > 4.0),
                    reasons=json.dumps(reasons),
                    status=status,
                    created_at=created_dt
                )
                batch.append(txn)
                
                if level == 'HIGH RISK' or (is_fraud or ratio > 4.0):
                    alert = FraudAlert(
                        transaction_id=str(row['transaction_id']),
                        alert_type='HIGH_RISK_SUSPICIOUS' if level == 'HIGH RISK' else 'ANOMALY_PATTERN',
                        severity='HIGH' if level == 'HIGH RISK' else 'MEDIUM',
                        message=f"Transaction {row['transaction_id']} flagged with risk score {round(score, 1)}%",
                        created_at=created_dt
                    )
                    alerts.append(alert)

                if len(batch) >= 2000:
                    db.session.bulk_save_objects(batch)
                    db.session.bulk_save_objects(alerts)
                    db.session.commit()
                    batch = []
                    alerts = []
                    
            if batch:
                db.session.bulk_save_objects(batch)
                db.session.bulk_save_objects(alerts)
                db.session.commit()
                
            print(f"Database seeded successfully with {Transaction.query.count()} records!")

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
