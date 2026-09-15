import os
from flask import Blueprint, jsonify, request
from services.risk_engine import RiskEngine
from services.transaction_service import TransactionService

checker_bp = Blueprint('checker_api', __name__, url_prefix='/api')

risk_engine = RiskEngine()

DEMO_SCENARIOS = {
    'safe': {
        'title': '🟢 Safe Payment Preset',
        'amount': 2500,
        'location': 'Hyderabad',
        'device': 'Known Phone',
        'payment_method': 'UPI',
        'hour': 14,
        'avg_amount': 2500,
        'new_device': False,
        'location_change': False,
        'transactions_last_10min': 1
    },
    'suspicious': {
        'title': '🟡 Suspicious Payment Preset',
        'amount': 30000,
        'location': 'Mumbai',
        'device': 'New Phone',
        'payment_method': 'Credit Card',
        'hour': 23,
        'avg_amount': 2500,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 4
    },
    'high_risk': {
        'title': '🔴 High Risk Payment Preset',
        'amount': 85000,
        'location': 'Singapore',
        'device': 'Unknown Web Browser',
        'payment_method': 'Net Banking',
        'hour': 3,
        'avg_amount': 2500,
        'new_device': True,
        'location_change': True,
        'transactions_last_10min': 6
    }
}

@checker_bp.route('/check', methods=['POST'])
def check_transaction():
    """Runs ML risk evaluation, saves transaction to DB, and returns results."""
    try:
        data = request.get_json() or {}
        
        # Input Validation
        try:
            amount = float(data.get('amount', 0))
            if amount <= 0:
                return jsonify({'success': False, 'error': 'Please enter a valid payment amount greater than zero.'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Please enter a valid numeric payment amount.'}), 400

        # Evaluate risk using centralized risk engine
        risk_result = risk_engine.evaluate_transaction(data)
        
        # Save transaction to database
        saved_txn = TransactionService.save_transaction(data, risk_result)
        
        return jsonify({
            'success': True,
            'data': {
                'transaction': saved_txn,
                'risk': risk_result
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f"Transaction check failed: {str(e)}"}), 500

@checker_bp.route('/demo-presets', methods=['GET'])
def get_demo_presets():
    """Returns pre-built demo scenarios for instant hackathon testing."""
    return jsonify({'success': True, 'data': DEMO_SCENARIOS})

from services.ai_service import AIService

@checker_bp.route('/ai/investigate', methods=['POST'])
def ai_investigate():
    """
    Deterministic AI Investigation Assistant.
    Analyzes exact transaction facts, risk engine calculations, and model outputs.
    Does not hallucinate or invent non-existent evidence.
    """
    try:
        data = request.get_json() or {}
        txn_id = data.get('transaction_id') or data.get('txn_id')
        question = data.get('question') or data.get('query') or ''

        res = AIService.generate_investigation(
            transaction_id=txn_id,
            question=question,
            raw_data=data
        )
        return jsonify(res), 200

    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f"Unable to investigate transaction: {str(e)}"}), 500
