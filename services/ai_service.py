import json
from typing import Dict, Any, Optional
from services.transaction_service import TransactionService
from services.risk_engine import RiskEngine

class AIService:
    @staticmethod
    def generate_investigation(
        transaction_id: Optional[str] = None,
        question: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deterministic, local AI Investigation Engine.
        Analyzes real transaction parameters, model predictions, anomaly scores, and DB facts.
        Operates without external API keys or external LLM dependencies.
        """
        txn = None
        if transaction_id:
            txn = TransactionService.get_transaction_by_id(str(transaction_id).strip())

        # Fallback if raw transaction data is passed directly
        if not txn and raw_data and isinstance(raw_data, dict) and raw_data.get('amount'):
            risk_engine = RiskEngine()
            risk_result = risk_engine.evaluate_transaction(raw_data)
            txn = {
                'transaction_id': str(raw_data.get('transaction_id') or 'CHECK_TEMP').strip(),
                'amount': float(raw_data.get('amount', 0.0)),
                'avg_amount': float(raw_data.get('avg_amount', 2500.0)),
                'amount_ratio': round(float(raw_data.get('amount', 0.0)) / (float(raw_data.get('avg_amount', 2500.0)) or 2500.0), 2),
                'location': str(raw_data.get('location', 'Unknown')),
                'device': str(raw_data.get('device', 'Unknown')),
                'payment_method': str(raw_data.get('payment_method', 'Credit Card')),
                'new_device': raw_data.get('new_device') in [True, 1, '1', 'Yes', 'yes', 'true'],
                'location_change': raw_data.get('location_change') in [True, 1, '1', 'Yes', 'yes', 'true'],
                'transactions_last_10min': int(raw_data.get('transactions_last_10min', 1)),
                'risk_score': risk_result['risk_score'],
                'risk_level': risk_result['risk_level'],
                'fraud_probability': risk_result['fraud_probability'],
                'is_anomaly': risk_result['is_anomaly'],
                'reasons': risk_result['reasons'],
                'status': 'UNDER_REVIEW' if risk_result['risk_level'] == 'CHECK' else ('BLOCKED' if risk_result['risk_level'] == 'HIGH RISK' else 'ALLOWED')
            }

        # Auto-fallback to suspicious or recent transactions if ID not provided or invalid
        if not txn:
            suspicious = TransactionService.get_suspicious_transactions(per_page=1)
            if suspicious.get('items'):
                txn = suspicious['items'][0]

        if not txn:
            all_txns = TransactionService.get_transactions(per_page=1)
            if all_txns.get('items'):
                txn = all_txns['items'][0]

        if not txn:
            raise ValueError("No transaction data available in the system to investigate.")

        # Parse reasons cleanly
        reasons_list = txn.get('reasons', [])
        if isinstance(reasons_list, str):
            try:
                reasons_list = json.loads(reasons_list)
            except Exception:
                reasons_list = [r.strip() for r in reasons_list.split(';') if r.strip()]

        if not reasons_list or not isinstance(reasons_list, list):
            reasons_list = ["Payment parameters match expected regular purchasing baseline."]

        reasons_bullets = "\n".join([f"• {r}" for r in reasons_list])

        q_lower = (question or '').lower().strip()
        txn_id_display = txn.get('transaction_id', 'UNKNOWN')
        amount_val = float(txn.get('amount', 0.0))
        avg_val = float(txn.get('avg_amount', 2500.0) or 2500.0)
        ratio_val = round(amount_val / avg_val, 1)
        risk_score = float(txn.get('risk_score', 0.0))
        risk_level = str(txn.get('risk_level', 'SAFE'))
        fraud_prob = float(txn.get('fraud_probability', 0.0))
        status_val = str(txn.get('status', 'ALLOWED'))
        loc_val = str(txn.get('location', 'Unknown'))
        dev_val = str(txn.get('device', 'Unknown'))
        method_val = str(txn.get('payment_method', 'Credit Card'))
        txns_10m = int(txn.get('transactions_last_10min', 1))
        is_new_dev = bool(txn.get('new_device'))
        is_new_loc = bool(txn.get('location_change'))
        is_anomaly_val = bool(txn.get('is_anomaly'))

        # Generate evidence-grounded answer based on query intent
        if any(w in q_lower for w in ['block', 'blocked', 'should', 'recommendation', 'override']):
            rec_action = "🚨 **BLOCK PAYMENT IMMEDIATELY**" if risk_level == 'HIGH RISK' else (
                "⚠️ **HOLD FOR MANUAL REVIEW**" if risk_level == 'CHECK' else "🟢 **ALLOW PAYMENT**"
            )
            answer = (
                f"### Actionable Recommendation & Block Status for `{txn_id_display}`\n\n"
                f"**System Recommendation:** {rec_action}\n"
                f"**Current Status:** `{status_val}`\n"
                f"**Risk Level:** {risk_level} (Score: {risk_score}%)\n\n"
                f"#### Key Block/Flag Reasons:\n{reasons_bullets}\n\n"
                f"#### Analyst Action Items:\n"
                f"1. Review device fingerprint (`{dev_val}`).\n"
                f"2. Confirm location coordinates ({loc_val}).\n"
                f"3. Use SOC Action drawer buttons (Allow / Review / Block) to record audit decision."
            )

        elif any(w in q_lower for w in ['why', 'flag', 'flagged', 'reason']):
            answer = (
                f"### Flagging Rationale for Transaction `{txn_id_display}`\n\n"
                f"**Assessed Risk Level:** {risk_level} (Score: {risk_score}%)\n"
                f"**Calculated Fraud Probability:** {fraud_prob}%\n\n"
                f"#### Triggered Empirical Risk Factors:\n{reasons_bullets}\n\n"
                f"**Behavioral Context:** Transaction of ₹{amount_val:,.2f} ({ratio_val}x usual avg of ₹{avg_val:,.2f}) "
                f"via {method_val} from {loc_val} using `{dev_val}`. "
                f"Velocity: {txns_10m} payments in last 10 mins."
            )

        elif any(w in q_lower for w in ['danger', 'dangerous', 'threat', 'safe']):
            severity_tag = "🚨 HIGH SEVERITY" if risk_level == 'HIGH RISK' else ("⚠️ MODERATE THREAT" if risk_level == 'CHECK' else "🟢 LOW THREAT")
            danger_explanation = (
                f"This transaction is {'dangerous' if risk_level == 'HIGH RISK' else 'flagged for caution'} because it has a risk score of {risk_score}% "
                f"and fraud probability of {fraud_prob}%. "
            )
            if risk_level == 'HIGH RISK':
                danger_explanation += f"The system detected high-risk behavioral activity ({'; '.join(reasons_list[:2])}). "
            else:
                danger_explanation += "The payment parameters align closely with baseline regular user activity. "

            danger_explanation += f"The transaction status is currently **{status_val}**."

            answer = (
                f"### Threat Assessment for Transaction `{txn_id_display}`\n\n"
                f"**Threat Level:** {severity_tag}\n"
                f"**Assessment:** {danger_explanation}\n\n"
                f"#### Evidence Factors:\n{reasons_bullets}\n\n"
                f"**Recommended Decision:** {'Keep transaction BLOCKED to prevent financial loss.' if status_val == 'BLOCKED' else 'Proceed with standard processing.'}"
            )

        elif any(w in q_lower for w in ['compare', 'normal', 'baseline', 'history']):
            answer = (
                f"### Historical Baseline Comparison for `{txn_id_display}`\n\n"
                f"• **Current Payment Amount:** ₹{amount_val:,.2f} vs Historical Average ₹{avg_val:,.2f} ({ratio_val}x ratio)\n"
                f"• **Device Fingerprint:** `{dev_val}` ({'Unrecognized Hardware' if is_new_dev else 'Recognized Usual Device'})\n"
                f"• **Geographic Location:** {loc_val} ({'New/Unusual Location' if is_new_loc else 'Normal Location'})\n"
                f"• **Velocity:** {txns_10m} transactions initiated in past 10 minutes\n\n"
                f"**Baseline Evaluation:** {'High deviation from normal purchasing habits.' if ratio_val > 3.0 or is_new_dev else 'Consistent with standard account history.'}"
            )

        else:
            answer = (
                f"### Investigation Report for Transaction `{txn_id_display}`\n\n"
                f"**Risk Assessment:** {risk_level} (Risk Score: {risk_score}%)\n"
                f"**Fraud Probability:** {fraud_prob}%\n"
                f"**Payment Amount:** ₹{amount_val:,.2f} via {method_val}\n"
                f"**Location & Device:** {loc_val} using `{dev_val}`\n"
                f"**Current Status:** {status_val}\n\n"
                f"#### Empirical Key Risk Factors:\n{reasons_bullets}\n\n"
                f"#### Recommended Action:\n"
            )
            if risk_level == 'HIGH RISK':
                answer += (
                    "🚨 **Block Payment**: High risk score detected due to severe behavioral deviation. "
                    "Immediate cardholder verification required before proceeding."
                )
            elif risk_level == 'CHECK':
                answer += (
                    "⚠️ **Review Payment**: Unusual parameters observed. Perform OTP or identity verification to confirm user intent."
                )
            else:
                answer += (
                    "🟢 **Allow Payment**: Transaction aligns with established baseline activity patterns. Low security concern."
                )

        return {
            'success': True,
            'answer': answer,
            'data': {
                'transaction_id': txn_id_display,
                'answer': answer,
                'transaction': txn,
                'is_deterministic': True
            },
            'transaction': txn
        }
