from ml.preprocessing import prepare_feature_dict

def generate_explanations(raw_data: dict, fraud_prob: float, is_anomaly: bool) -> dict:
    """
    Generates dynamic, human-understandable risk reasons and technical feature contributions.
    Returns:
        {
            'user_reasons': list of simple string explanations,
            'technical_details': dict with feature values and risk contribution scores
        }
    """
    feat = prepare_feature_dict(raw_data)
    user_reasons = []
    technical = {}
    
    amount = feat['amount']
    avg_amount = feat['avg_amount']
    amount_ratio = feat['amount_ratio']
    new_device = feat['new_device']
    location_change = feat['location_change']
    txns_10m = feat['transactions_last_10min']
    hour = feat['hour']
    is_night = feat['is_night_time']
    
    # 1. Amount Anomaly check
    if amount_ratio >= 5.0:
        user_reasons.append(f"The payment amount (₹{amount:,.2f}) is over {amount_ratio:.1f}x higher than your usual average.")
        technical['amount_contribution'] = 'HIGH_SPIKE'
    elif amount_ratio >= 2.5:
        user_reasons.append(f"The payment amount is significantly higher than your typical average.")
        technical['amount_contribution'] = 'MODERATE_SPIKE'
    else:
        technical['amount_contribution'] = 'NORMAL'
        
    # 2. Device Novelty check
    if new_device:
        user_reasons.append("An unrecognized or new device was used for this transaction.")
        technical['device_status'] = 'NEW_UNRECOGNIZED_DEVICE'
    else:
        technical['device_status'] = 'KNOWN_TRUSTED_DEVICE'
        
    # 3. Location Anomaly check
    if location_change:
        user_reasons.append(f"This payment occurred from an unusual or unverified location ({raw_data.get('location', 'Unusual location')}).")
        technical['location_status'] = 'UNUSUAL_GEO_LOCATION'
    else:
        technical['location_status'] = 'REGULAR_LOCATION'
        
    # 4. Velocity check
    if txns_10m >= 5:
        user_reasons.append(f"High activity: {txns_10m} payments were initiated in the last 10 minutes.")
        technical['velocity_risk'] = 'CRITICAL_HIGH_VELOCITY'
    elif txns_10m >= 3:
        user_reasons.append(f"Multiple payments ({txns_10m}) occurred in a short time frame.")
        technical['velocity_risk'] = 'ELEVATED_VELOCITY'
    else:
        technical['velocity_risk'] = 'NORMAL_VELOCITY'
        
    # 5. Unusual Time check
    if is_night:
        user_reasons.append(f"The payment occurred during unusual night-time hours ({hour:02d}:00).")
        technical['time_risk'] = 'OFF_HOURS_NIGHT'
    else:
        technical['time_risk'] = 'REGULAR_HOURS'
        
    # 6. Unsupervised Anomaly Model signal
    if is_anomaly:
        user_reasons.append("The overall payment pattern differs from normal transaction behavior.")
        technical['isolation_forest'] = 'ANOMALOUS_PATTERN_DETECTED'
    else:
        technical['isolation_forest'] = 'NORMAL_PATTERN'
        
    # Default fallback if low risk and no flags triggered
    if not user_reasons:
        user_reasons.append("Payment matches expected regular purchasing behavior.")
        
    return {
        'user_reasons': user_reasons,
        'technical_details': technical,
        'fraud_probability_percent': round(fraud_prob * 100, 1),
        'is_anomaly': is_anomaly
    }
