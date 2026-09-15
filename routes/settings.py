import json
from flask import Blueprint, jsonify, request
from database.schema import db, Setting

settings_bp = Blueprint('settings_api', __name__, url_prefix='/api/settings')

DEFAULT_SETTINGS = {
    'notifications_safety': 'ON',
    'notifications_high_risk': 'ON',
    'appearance_theme': 'light',
    'auto_block_threshold': '65',
    'security_session_timeout': '30'
}

@settings_bp.route('', methods=['GET'])
def get_settings():
    """Returns application preferences."""
    try:
        settings_objs = Setting.query.all()
        settings_dict = DEFAULT_SETTINGS.copy()
        for s in settings_objs:
            settings_dict[s.key] = s.value
        return jsonify({'success': True, 'data': settings_dict})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('', methods=['PUT'])
def update_settings():
    """Updates key-value settings in database."""
    try:
        data = request.get_json() or {}
        for key, value in data.items():
            setting = Setting.query.filter_by(key=key).first()
            if not setting:
                setting = Setting(key=key, value=str(value))
                db.session.add(setting)
            else:
                setting.value = str(value)
        db.session.commit()
        
        # Return updated list
        settings_objs = Setting.query.all()
        settings_dict = DEFAULT_SETTINGS.copy()
        for s in settings_objs:
            settings_dict[s.key] = s.value
            
        return jsonify({'success': True, 'message': 'Settings updated successfully', 'data': settings_dict})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
