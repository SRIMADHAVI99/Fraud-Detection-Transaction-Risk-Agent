import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import or_, desc, asc, func
from database.schema import db, Transaction, FraudAlert, Action


def random_id() -> str:
    """Generates a random 6-digit numeric string for default transaction IDs."""
    return str(uuid.uuid4().int)[:6]


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely converts input to float with fallback default."""
    try:
        if val is None:
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val: Any, default: int = 1) -> int:
    """Safely converts input to int with fallback default."""
    try:
        if val is None:
            return default
        return int(val)
    except (ValueError, TypeError):
        return default


class TransactionService:
    @staticmethod
    def get_stats() -> Dict[str, int]:
        """Calculates overview statistics for monitored transactions."""
        total = db.session.query(func.count(Transaction.id)).scalar() or 0
        safe = db.session.query(func.count(Transaction.id)).filter(Transaction.risk_level == 'SAFE').scalar() or 0
        check = db.session.query(func.count(Transaction.id)).filter(Transaction.risk_level == 'CHECK').scalar() or 0
        high_risk = db.session.query(func.count(Transaction.id)).filter(Transaction.risk_level == 'HIGH RISK').scalar() or 0
        fraud_alerts = db.session.query(func.count(FraudAlert.id)).scalar() or 0
        blocked = db.session.query(func.count(Transaction.id)).filter(Transaction.status == 'BLOCKED').scalar() or 0
        under_review = db.session.query(func.count(Transaction.id)).filter(Transaction.status == 'UNDER_REVIEW').scalar() or 0

        return {
            'total_transactions': total,
            'safe_payments': safe,
            'need_checking': check,
            'fraud_alerts': high_risk,
            'blocked_payments': blocked,
            'under_review': under_review
        }

    @staticmethod
    def get_transactions(
        page: int = 1,
        per_page: int = 15,
        search: str = '',
        risk_level: str = '',
        payment_method: str = '',
        status: str = '',
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Dict[str, Any]:
        """Fetches paginated transactions with optional search, filtering, and sorting."""
        query = Transaction.query

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.transaction_id.ilike(search_pattern),
                    Transaction.location.ilike(search_pattern),
                    Transaction.device.ilike(search_pattern),
                    Transaction.payment_method.ilike(search_pattern)
                )
            )

        if risk_level:
            query = query.filter(Transaction.risk_level == risk_level)

        if payment_method:
            query = query.filter(Transaction.payment_method == payment_method)

        if status:
            query = query.filter(Transaction.status == status)

        sort_attr = getattr(Transaction, sort_by, Transaction.created_at)
        if sort_order.lower() == 'asc':
            query = query.order_by(asc(sort_attr))
        else:
            query = query.order_by(desc(sort_attr))

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'items': [item.to_dict() for item in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def get_transaction_by_id(txn_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single transaction details by its unique identifier."""
        txn = Transaction.query.filter_by(transaction_id=txn_id).first()
        return txn.to_dict() if txn else None

    @staticmethod
    def get_suspicious_transactions(search: str = '', page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """Fetches suspicious payments and anomalies for Threat Center viewing."""
        query = Transaction.query.filter(
            or_(
                Transaction.risk_level.in_(['CHECK', 'HIGH RISK']),
                Transaction.is_anomaly.is_(True)
            )
        ).order_by(desc(Transaction.risk_score))

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.transaction_id.ilike(search_pattern),
                    Transaction.location.ilike(search_pattern),
                    Transaction.device.ilike(search_pattern)
                )
            )

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [item.to_dict() for item in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }

    @staticmethod
    def save_transaction(raw_data: dict, risk_result: dict, status: Optional[str] = None) -> dict:
        """Saves a new transaction record and associated fraud alerts to the database."""
        txn_id = raw_data.get('transaction_id') or raw_data.get('register_id') or raw_data.get('txn_id')
        if not txn_id or not str(txn_id).strip():
            txn_id = f"TXN{random_id()}"
        else:
            txn_id = str(txn_id).strip()

        if not status:
            if risk_result['risk_level'] == 'HIGH RISK':
                status = 'BLOCKED'
            elif risk_result['risk_level'] == 'CHECK':
                status = 'UNDER_REVIEW'
            else:
                status = 'ALLOWED'

        now_dt = datetime.now()
        amount_val = _safe_float(raw_data.get('amount'), 0.0)
        avg_amount_val = _safe_float(raw_data.get('avg_amount'), 2500.0)
        if avg_amount_val <= 0:
            avg_amount_val = 2500.0

        amount_ratio_val = round(amount_val / avg_amount_val, 2)

        existing_txn = Transaction.query.filter_by(transaction_id=txn_id).first()

        if existing_txn:
            existing_txn.amount = amount_val
            existing_txn.location = str(raw_data.get('location', 'Unknown'))
            existing_txn.device = str(raw_data.get('device', 'Unknown'))
            existing_txn.payment_method = str(raw_data.get('payment_method', 'Credit Card'))
            existing_txn.hour = _safe_int(raw_data.get('hour'), now_dt.hour)
            existing_txn.avg_amount = avg_amount_val
            existing_txn.amount_ratio = amount_ratio_val
            existing_txn.new_device = raw_data.get('new_device') in [True, 1, '1', 'Yes', 'yes', 'true']
            existing_txn.location_change = raw_data.get('location_change') in [True, 1, '1', 'Yes', 'yes', 'true']
            existing_txn.transactions_last_10min = _safe_int(raw_data.get('transactions_last_10min'), 1)
            existing_txn.risk_score = risk_result['risk_score']
            existing_txn.risk_level = risk_result['risk_level']
            existing_txn.fraud_probability = risk_result['fraud_probability']
            existing_txn.is_anomaly = risk_result['is_anomaly']
            existing_txn.reasons = json.dumps(risk_result['reasons'])
            existing_txn.status = status
            existing_txn.updated_at = now_dt
            txn = existing_txn
        else:
            txn = Transaction(
                transaction_id=txn_id,
                amount=amount_val,
                location=str(raw_data.get('location', 'Unknown')),
                device=str(raw_data.get('device', 'Unknown')),
                payment_method=str(raw_data.get('payment_method', 'Credit Card')),
                hour=_safe_int(raw_data.get('hour'), now_dt.hour),
                avg_amount=avg_amount_val,
                amount_ratio=amount_ratio_val,
                new_device=raw_data.get('new_device') in [True, 1, '1', 'Yes', 'yes', 'true'],
                location_change=raw_data.get('location_change') in [True, 1, '1', 'Yes', 'yes', 'true'],
                transactions_last_10min=_safe_int(raw_data.get('transactions_last_10min'), 1),
                risk_score=risk_result['risk_score'],
                risk_level=risk_result['risk_level'],
                fraud_probability=risk_result['fraud_probability'],
                is_anomaly=risk_result['is_anomaly'],
                reasons=json.dumps(risk_result['reasons']),
                status=status,
                created_at=now_dt
            )
            db.session.add(txn)

        if risk_result['risk_level'] == 'HIGH RISK' or risk_result['is_anomaly']:
            alert_msg = (
                f"Transaction {txn_id} flagged with risk score {risk_result['risk_score']}%: "
                f"{'; '.join(risk_result['reasons'])}"
            )
            alert = FraudAlert(
                transaction_id=txn_id,
                alert_type='HIGH_RISK_SUSPICIOUS' if risk_result['risk_level'] == 'HIGH RISK' else 'ANOMALY_PATTERN',
                severity='HIGH' if risk_result['risk_level'] == 'HIGH RISK' else 'MEDIUM',
                message=alert_msg,
                created_at=now_dt
            )
            db.session.add(alert)

        db.session.commit()
        return txn.to_dict()

    @staticmethod
    def update_action(txn_id: str, action_type: str, notes: str = '') -> dict:
        """Updates decision status for a transaction and logs analyst audit action."""
        txn = Transaction.query.filter_by(transaction_id=txn_id).first()
        if not txn:
            raise ValueError(f"Transaction {txn_id} not found.")

        status_map = {
            'ALLOW': 'ALLOWED',
            'REVIEW': 'UNDER_REVIEW',
            'BLOCK': 'BLOCKED'
        }

        new_status = status_map.get(action_type.upper(), 'UNDER_REVIEW')
        txn.status = new_status
        txn.updated_at = datetime.now()

        action = Action(
            transaction_id=txn_id,
            action_type=action_type.upper(),
            notes=notes,
            created_at=datetime.now()
        )
        db.session.add(action)
        db.session.commit()

        return txn.to_dict()

    @staticmethod
    def get_activity_data() -> Dict[str, Any]:
        """Aggregates analytics data for charts, trends, and recent activity feeds."""
        safe_cnt = Transaction.query.filter_by(risk_level='SAFE').count()
        check_cnt = Transaction.query.filter_by(risk_level='CHECK').count()
        high_cnt = Transaction.query.filter_by(risk_level='HIGH RISK').count()

        methods = db.session.query(
            Transaction.payment_method, func.count(Transaction.id)
        ).group_by(Transaction.payment_method).all()

        method_labels = [m[0] for m in methods]
        method_counts = [m[1] for m in methods]

        recent_dates_query = db.session.query(
            func.date(Transaction.created_at)
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by(
            desc(func.date(Transaction.created_at))
        ).limit(7).all()

        raw_date_strings = [r[0] for r in reversed(recent_dates_query)] if recent_dates_query else []

        dates = []
        safe_series = []
        risk_series = []

        for d_str in raw_date_strings:
            try:
                dt_obj = datetime.strptime(str(d_str), '%Y-%m-%d')
                dates.append(dt_obj.strftime('%b %d'))
            except ValueError:
                dates.append(str(d_str))

            day_start = datetime.strptime(f"{d_str} 00:00:00", '%Y-%m-%d %H:%M:%S')
            day_end = datetime.strptime(f"{d_str} 23:59:59", '%Y-%m-%d %H:%M:%S')

            day_safe = Transaction.query.filter(
                Transaction.created_at >= day_start,
                Transaction.created_at <= day_end,
                Transaction.risk_level == 'SAFE'
            ).count()

            day_risk = Transaction.query.filter(
                Transaction.created_at >= day_start,
                Transaction.created_at <= day_end,
                Transaction.risk_level.in_(['CHECK', 'HIGH RISK'])
            ).count()

            safe_series.append(day_safe)
            risk_series.append(day_risk)

        recent_events = []
        recent_flagged = Transaction.query.order_by(desc(Transaction.created_at)).limit(6).all()
        for t in recent_flagged:
            time_str = t.created_at.strftime('%I:%M %p') if t.created_at else 'Just now'
            icon = '🔴' if t.risk_level == 'HIGH RISK' else ('🟡' if t.risk_level == 'CHECK' else '🟢')

            reason_str = 'Transaction processed'
            if t.reasons:
                try:
                    parsed_reasons = json.loads(t.reasons)
                    if parsed_reasons and isinstance(parsed_reasons, list):
                        reason_str = parsed_reasons[0]
                except (json.JSONDecodeError, TypeError):
                    pass

            recent_events.append({
                'time': time_str,
                'title': f"{icon} {t.risk_level} — {t.transaction_id}",
                'subtitle': f"₹{t.amount:,.2f} • {t.location} • {t.device}",
                'reason': reason_str
            })

        return {
            'risk_distribution': {
                'labels': ['Safe', 'Need Checking', 'High Risk'],
                'data': [safe_cnt, check_cnt, high_cnt]
            },
            'payment_methods': {
                'labels': method_labels,
                'data': method_counts
            },
            'trend': {
                'dates': dates,
                'safe': safe_series,
                'suspicious': risk_series
            },
            'recent_events': recent_events
        }
