from flask import Blueprint, jsonify, send_file
from services.transaction_service import TransactionService
from services.report_service import ReportService

reports_bp = Blueprint('reports_api', __name__, url_prefix='/api/reports')

@reports_bp.route('', methods=['GET'])
def get_reports_summary():
    """Returns summary metrics for reports view."""
    try:
        stats = TransactionService.get_stats()
        suspicious = TransactionService.get_suspicious_transactions(per_page=10)
        return jsonify({
            'success': True,
            'data': {
                'stats': stats,
                'recent_suspicious': suspicious['items']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@reports_bp.route('/download', methods=['GET'])
def download_pdf_report():
    """Generates and downloads a complete ReportLab PDF security report."""
    try:
        pdf_buffer = ReportService.generate_pdf_report()
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"FraudGuard_Security_Report_{TransactionService.get_stats()['total_transactions']}_txns.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
