from flask import Blueprint, jsonify, request
from services.transaction_service import TransactionService

transactions_bp = Blueprint('transactions_api', __name__, url_prefix='/api')

@transactions_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """Returns searchable, filterable, paginated transaction history."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        search = request.args.get('search', '', type=str)
        risk_level = request.args.get('risk_level', '', type=str)
        payment_method = request.args.get('payment_method', '', type=str)
        status = request.args.get('status', '', type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        result = TransactionService.get_transactions(
            page=page,
            per_page=per_page,
            search=search,
            risk_level=risk_level,
            payment_method=payment_method,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_bp.route('/transactions/<txn_id>', methods=['GET'])
def get_transaction_detail(txn_id):
    """Returns detail for a single transaction."""
    try:
        txn = TransactionService.get_transaction_by_id(txn_id)
        if not txn:
            return jsonify({'success': False, 'error': f'Transaction {txn_id} not found'}), 404
        return jsonify({'success': True, 'data': txn})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_bp.route('/transactions/<txn_id>/action', methods=['POST'])
def update_transaction_action(txn_id):
    """Executes manual decision action (ALLOW, REVIEW, BLOCK) on a transaction."""
    try:
        data = request.get_json() or {}
        action_type = data.get('action') or data.get('action_type')
        notes = data.get('notes', '')

        if not action_type or action_type.upper() not in ['ALLOW', 'REVIEW', 'BLOCK']:
            return jsonify({
                'success': False,
                'error': 'Action must be one of: ALLOW, REVIEW, BLOCK'
            }), 400

        updated_txn = TransactionService.update_action(txn_id, action_type, notes)
        return jsonify({
            'success': True,
            'message': f"Transaction {txn_id} status updated to {updated_txn['status']}",
            'data': updated_txn
        })
    except ValueError as ve:
        return jsonify({'success': False, 'error': str(ve)}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@transactions_bp.route('/suspicious', methods=['GET'])
def get_suspicious():
    """Returns list of suspicious and anomalous transactions."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 15, type=int)
        search = request.args.get('search', '', type=str)
        
        result = TransactionService.get_suspicious_transactions(search=search, page=page, per_page=per_page)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
