/* FRAUDGUARD AI — Safety Checker & Animated Gauge JS */

let lastCheckedTxnId = null;

async function handleSafetyCheck(e) {
  e.preventDefault();
  const output = document.getElementById('safety-result-output');
  const loaderContainer = document.getElementById('safety-loader-container');
  const btn = document.getElementById('sc-submit-btn');

  const customTxnId = document.getElementById('sc-txn-id')?.value.trim();

  const payload = {
    transaction_id: customTxnId || undefined,
    amount: parseFloat(document.getElementById('sc-amount').value),
    location: document.getElementById('sc-location').value,
    device: document.getElementById('sc-device').value,
    payment_method: document.getElementById('sc-method').value,
    avg_amount: parseFloat(document.getElementById('sc-avg-amount').value || 2500),
    new_device: document.getElementById('sc-new-device').value === 'true',
    location_change: document.getElementById('sc-new-location').value === 'true',
    transactions_last_10min: parseInt(document.getElementById('sc-txns-10m').value || 1)
  };

  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Checking safety...`;
  
  if (loaderContainer) loaderContainer.style.display = 'block';
  if (output) output.innerHTML = '';

  // Active step sequence tied to async request
  const step1 = document.getElementById('step-1');
  const step2 = document.getElementById('step-2');
  const step3 = document.getElementById('step-3');
  const step4 = document.getElementById('step-4');
  const step5 = document.getElementById('step-5');

  if (step1) step1.className = 'loader-step-item active';
  
  try {
    // Send real check request to backend
    const checkPromise = fetch('/api/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });

    if (step2) setTimeout(() => step2.className = 'loader-step-item active', 150);
    if (step3) setTimeout(() => step3.className = 'loader-step-item active', 300);
    if (step4) setTimeout(() => step4.className = 'loader-step-item active', 450);
    if (step5) setTimeout(() => step5.className = 'loader-step-item active', 600);

    const res = await checkPromise;
    const json = await res.json();

    if (!json.success) {
      showToast(json.error || 'Check failed', 'error');
      return;
    }

    const txn = json.data.transaction;
    const risk = json.data.risk;
    lastCheckedTxnId = txn.transaction_id;

    let bannerBorder = 'var(--risk-safe-border)';
    let bannerBg = 'var(--risk-safe-bg)';
    let gaugeColor = 'var(--risk-safe)';
    let titleText = '✓ SAFE PAYMENT';
    let subText = 'This payment matches expected regular purchasing behavior.';

    if (risk.risk_level === 'CHECK') {
      bannerBorder = 'var(--risk-check-border)';
      bannerBg = 'var(--risk-check-bg)';
      gaugeColor = 'var(--risk-check)';
      titleText = '⚠ CHECK THIS PAYMENT';
      subText = 'This payment exhibits unusual behavioral parameters.';
    } else if (risk.risk_level === 'HIGH RISK') {
      bannerBorder = 'var(--risk-high-border)';
      bannerBg = 'var(--risk-high-bg)';
      gaugeColor = 'var(--risk-high)';
      titleText = '🚨 HIGH RISK';
      subText = 'This payment exhibits strong indicators of potential fraud.';
    }

    const reasonsList = (risk.reasons || []).map(r => `<li style="margin-bottom:6px;">✓ ${r}</li>`).join('');

    // Radius r=54 -> Circumference C = 2 * PI * 54 = 339.29
    const circumference = 339.29;
    const targetOffset = circumference - ((risk.risk_score / 100) * circumference);

    output.innerHTML = `
      <div style="background-color: var(--bg-surface); border: 1px solid ${bannerBorder}; border-radius: 12px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 20px; margin-bottom: 20px;">
          
          <div style="display: flex; align-items: center; gap: 24px;">
            <!-- Radial SVG Gauge -->
            <div class="gauge-container">
              <svg class="gauge-svg" viewBox="0 0 120 120">
                <circle class="gauge-bg-circle" cx="60" cy="60" r="54"/>
                <circle class="gauge-fill-circle" id="risk-gauge-fill" cx="60" cy="60" r="54" style="stroke: ${gaugeColor};"/>
              </svg>
              <div class="gauge-text">
                <div class="gauge-value" style="color: ${gaugeColor};">${risk.risk_score}%</div>
                <div class="gauge-label">${risk.risk_level}</div>
              </div>
            </div>

            <div>
              <h2 style="font-size: 1.4rem; font-weight: 800; color: ${gaugeColor}; margin-bottom: 4px;">${titleText}</h2>
              <div style="font-size: 0.9rem; color: var(--text-main); font-weight: 600;">Risk Score: ${risk.risk_score} / 100</div>
              <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 2px;">"${subText}"</div>
            </div>
          </div>

          <div style="font-size: 0.82rem; color: var(--text-muted); text-align: right;">
            <div>Transaction ID: <strong style="color:var(--text-main);">${txn.transaction_id}</strong></div>
            <div>Fraud Probability: <strong style="color:var(--cyan-accent);">${risk.fraud_probability}%</strong></div>
            <div>Anomaly Status: <strong style="color:var(--text-main);">${risk.is_anomaly ? 'Outlier Pattern' : 'Inlier Baseline'}</strong></div>
          </div>
        </div>

        <!-- Evidence Panel: WHY THIS PAYMENT WAS FLAGGED -->
        <div style="background-color: var(--bg-card); border: 1px solid var(--border-subtle); padding: 18px; border-radius: 8px; margin-bottom: 20px;">
          <div style="font-weight: 700; font-size: 0.88rem; color: var(--cyan-accent); margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">
            <i class="fa-solid fa-microchip"></i> WHY THIS PAYMENT WAS FLAGGED (RISK EVIDENCE)
          </div>
          <ul style="padding-left: 0; list-style: none; font-size: 0.88rem; color: var(--text-main);">
            ${reasonsList || '<li>✓ Parameters align with expected standard behavior</li>'}
          </ul>
        </div>

        <!-- Action Panel -->
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <button class="btn btn-success" style="flex:1;" onclick="takeActionSafetyCheck('${txn.transaction_id}', 'ALLOW')">
            <i class="fa-solid fa-check"></i> ALLOW PAYMENT
          </button>
          <button class="btn btn-warning" style="flex:1;" onclick="takeActionSafetyCheck('${txn.transaction_id}', 'REVIEW')">
            <i class="fa-solid fa-eye"></i> REVIEW PAYMENT
          </button>
          <button class="btn btn-danger" style="flex:1;" onclick="takeActionSafetyCheck('${txn.transaction_id}', 'BLOCK')">
            <i class="fa-solid fa-ban"></i> BLOCK PAYMENT
          </button>
        </div>
      </div>
    `;

    // Trigger SVG gauge stroke animation to actual score
    setTimeout(() => {
      const fillCircle = document.getElementById('risk-gauge-fill');
      if (fillCircle) {
        fillCircle.style.strokeDashoffset = targetOffset;
      }
    }, 100);

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    if (loaderContainer) loaderContainer.style.display = 'none';
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-shield-halved"></i> CHECK PAYMENT NOW`;
  }
}

async function takeActionSafetyCheck(txnId, actionType) {
  try {
    const res = await fetch(`/api/transactions/${txnId}/action`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: actionType})
    });
    const json = await res.json();
    if (json.success) {
      showToast(`Transaction ${txnId} status updated to ${json.data.status}`, 'success');
    } else {
      showToast(json.error, 'error');
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}
