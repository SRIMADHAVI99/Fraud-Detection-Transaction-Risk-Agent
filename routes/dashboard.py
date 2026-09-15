from flask import Blueprint, jsonify, request
from services.transaction_service import TransactionService

dashboard_bp = Blueprint('dashboard_api', __name__, url_prefix='/api')

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Returns dynamic statistics for dashboard summary cards."""
    try:
        stats = TransactionService.get_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/recent-transactions', methods=['GET'])
def get_recent_transactions():
    """Returns top 5 most recent transactions for home dashboard."""
    try:
        limit = request.args.get('limit', 5, type=int)
        res = TransactionService.get_transactions(page=1, per_page=limit, sort_by='created_at', sort_order='desc')
        return jsonify({'success': True, 'data': res['items']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@dashboard_bp.route('/activity', methods=['GET'])
def get_activity():
    """Returns chart analytics data."""
    try:
        activity_data = TransactionService.get_activity_data()
        return jsonify({'success': True, 'data': activity_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
