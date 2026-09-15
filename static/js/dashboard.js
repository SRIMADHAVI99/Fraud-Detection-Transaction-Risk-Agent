/* FRAUDGUARD AI — Overview Dashboard JS */

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardStats();
  loadRecentPayments();
  loadDashboardCharts();
});

// 1. Load Stats
async function loadDashboardStats() {
  try {
    const res = await fetch('/api/stats');
    const json = await res.json();
    if (json.success) {
      const d = json.data;
      document.getElementById('stat-total-payments').textContent = d.total_transactions.toLocaleString('en-IN');
      document.getElementById('stat-safe-payments').textContent = d.safe_payments.toLocaleString('en-IN');
      document.getElementById('stat-need-checking').textContent = d.need_checking.toLocaleString('en-IN');
      document.getElementById('stat-fraud-alerts').textContent = d.fraud_alerts.toLocaleString('en-IN');
    }
  } catch (err) {
    console.error('Failed to load dashboard stats', err);
  }
}

// 2. Load Recent Payments Table
async function loadRecentPayments() {
  const tbody = document.getElementById('recent-payments-tbody');
  if (!tbody) return;

  try {
    const res = await fetch('/api/recent-transactions?limit=6');
    const json = await res.json();

    if (!json.success || !json.data.length) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px;">No payments recorded.</td></tr>`;
      return;
    }

    tbody.innerHTML = json.data.map(item => {
      let badgeClass = 'badge-risk-safe';
      if (item.risk_level === 'CHECK') badgeClass = 'badge-risk-check';
      if (item.risk_level === 'HIGH RISK') badgeClass = 'badge-risk-high';

      return `
        <tr onclick="openInvestigationDrawer('${item.transaction_id}')">
          <td><strong>${item.transaction_id}</strong></td>
          <td>₹${item.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          <td>${item.location}</td>
          <td>${item.payment_method}</td>
          <td><span class="badge-risk ${badgeClass}">${item.risk_level} (${item.risk_score}%)</span></td>
          <td><span class="badge-status badge-status-${item.status.toLowerCase()}">${item.status}</span></td>
          <td>${item.created_at ? item.created_at.split(' ')[1] : 'Today'}</td>
          <td>
            <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); openInvestigationDrawer('${item.transaction_id}')">
              Details
            </button>
          </td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="color:var(--risk-high); text-align:center;">Failed to load recent payments.</td></tr>`;
  }
}

// 3. Load Charts & Recent Activity Feed
async function loadDashboardCharts() {
  try {
    const res = await fetch('/api/activity');
    const json = await res.json();
    if (!json.success || !json.data) return;

    const data = json.data;

    // Render Recent Activity Feed
    const feed = document.getElementById('recent-activity-feed');
    if (feed && data.recent_events) {
      feed.innerHTML = data.recent_events.map(ev => `
        <div style="background-color: var(--bg-surface); padding: 10px 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
          <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
            <strong style="color:var(--text-main); font-size:0.82rem;">${ev.title}</strong>
            <span style="color:var(--text-dim); font-size:0.72rem;">${ev.time}</span>
          </div>
          <div style="color:var(--text-muted); font-size:0.75rem;">${ev.subtitle}</div>
        </div>
      `).join('');
    }

    // Dashboard Donut Chart
    const ctxRisk = document.getElementById('dash-chart-risk');
    if (ctxRisk) {
      new Chart(ctxRisk.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: data.risk_distribution.labels,
          datasets: [{
            data: data.risk_distribution.data,
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
            borderWidth: 2,
            borderColor: '#0b1930'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }
        }
      });
    }

    // Dashboard Line Chart
    const ctxTrend = document.getElementById('dash-chart-trend');
    if (ctxTrend) {
      new Chart(ctxTrend.getContext('2d'), {
        type: 'line',
        data: {
          labels: data.trend.dates,
          datasets: [
            {
              label: 'Safe',
              data: data.trend.safe,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              fill: true,
              tension: 0.3
            },
            {
              label: 'Suspicious / High Risk',
              data: data.trend.suspicious,
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top', labels: { color: '#94a3b8' } } },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
          }
        }
      });
    }

  } catch (err) {
    console.error('Error loading dashboard charts', err);
  }
}

// 4. Demo Preset Selector
async function loadDemoScenario(type) {
  try {
    const res = await fetch('/api/demo-presets');
    const json = await res.json();
    if (json.success && json.data[type]) {
      const preset = json.data[type];
      
      const amtEl = document.getElementById('check-amount') || document.getElementById('sc-amount');
      const locEl = document.getElementById('check-location') || document.getElementById('sc-location');
      const devEl = document.getElementById('check-device') || document.getElementById('sc-device');
      const metEl = document.getElementById('check-method') || document.getElementById('sc-method');
      const avgEl = document.getElementById('check-avg-amount') || document.getElementById('sc-avg-amount');
      const newDevEl = document.getElementById('check-new-device') || document.getElementById('sc-new-device');
      const newLocEl = document.getElementById('check-new-location') || document.getElementById('sc-new-location');
      const txnsEl = document.getElementById('check-txns-10m') || document.getElementById('sc-txns-10m');

      if (amtEl) amtEl.value = preset.amount;
      if (locEl) locEl.value = preset.location;
      if (devEl) devEl.value = preset.device;
      if (metEl) metEl.value = preset.payment_method;
      if (avgEl) avgEl.value = preset.avg_amount;
      if (newDevEl) newDevEl.value = preset.new_device ? 'true' : 'false';
      if (newLocEl) newLocEl.value = preset.location_change ? 'true' : 'false';
      if (txnsEl) txnsEl.value = preset.transactions_last_10min;

      showToast(`Loaded ${preset.title}`, 'info');
    }
  } catch (err) {
    showToast('Failed to load demo scenario', 'error');
  }
}

// 5. Quick Check Submission Handler
async function handleQuickCheck(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('check-submit-btn');
  const resultContainer = document.getElementById('check-result-container');

  const customTxnId = document.getElementById('check-txn-id')?.value.trim();

  const payload = {
    transaction_id: customTxnId || undefined,
    amount: parseFloat(document.getElementById('check-amount').value),
    location: document.getElementById('check-location').value,
    device: document.getElementById('check-device').value,
    payment_method: document.getElementById('check-method').value,
    avg_amount: parseFloat(document.getElementById('check-avg-amount').value || 2500),
    new_device: document.getElementById('check-new-device').value === 'true',
    location_change: document.getElementById('check-new-location').value === 'true',
    transactions_last_10min: parseInt(document.getElementById('check-txns-10m').value || 1)
  };

  submitBtn.disabled = true;
  submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Checking payment...`;

  try {
    const res = await fetch('/api/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (!json.success) {
      showToast(json.error || 'Check failed', 'error');
      return;
    }

    const txn = json.data.transaction;
    const risk = json.data.risk;

    let bannerClass = 'result-banner-safe';
    let titleText = '🟢 SAFE PAYMENT';
    if (risk.risk_level === 'CHECK') bannerClass = 'result-banner-check', titleText = '🟡 CHECK THIS PAYMENT';
    if (risk.risk_level === 'HIGH RISK') bannerClass = 'result-banner-high', titleText = '🔴 HIGH RISK';

    const reasonsList = (risk.reasons || []).map(r => `<li>${r}</li>`).join('');

    resultContainer.style.display = 'block';
    resultContainer.innerHTML = `
      <div style="background-color: var(--bg-surface); border: 1px solid var(--border-cyan); border-radius: 8px; padding: 16px; font-size: 0.85rem;">
        <div style="font-weight: 700; font-size: 1rem; color: var(--text-main);">${titleText}</div>
        <div style="color: var(--cyan-accent); font-weight: 600; margin-top: 2px;">Risk Level: ${risk.risk_level} — Score: ${risk.risk_score}%</div>
        
        <ul style="padding-left: 18px; margin-top: 8px; color: var(--text-muted);">
          ${reasonsList || '<li>Normal payment behavior</li>'}
        </ul>

        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <button class="btn btn-success btn-sm" onclick="drawerTakeAction('${txn.transaction_id}', 'ALLOW')">Allow</button>
          <button class="btn btn-warning btn-sm" onclick="drawerTakeAction('${txn.transaction_id}', 'REVIEW')">Review</button>
          <button class="btn btn-danger btn-sm" onclick="drawerTakeAction('${txn.transaction_id}', 'BLOCK')">Block</button>
        </div>
      </div>
    `;

    loadDashboardStats();
    loadRecentPayments();

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> Check Now`;
  }
}

window.loadDashboardStats = loadDashboardStats;
window.loadRecentPayments = loadRecentPayments;
