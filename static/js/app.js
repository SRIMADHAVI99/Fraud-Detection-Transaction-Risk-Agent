/* FRAUDGUARD AI — Enterprise Helper JavaScript */

document.addEventListener('DOMContentLoaded', () => {
  // 0. Theme Initialization
  initTheme();

  // 1. Dynamic Live Clock
  initLiveClock();
  
  // 2. Mobile Sidebar Toggle
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }
});

// Theme Toggle Management
function applyTheme(theme) {
  if (theme === 'light') {
    document.documentElement.classList.add('light-theme');
    document.body.classList.add('light-theme');
    localStorage.setItem('fraudguard_theme', 'light');
  } else {
    document.documentElement.classList.remove('light-theme');
    document.body.classList.remove('light-theme');
    localStorage.setItem('fraudguard_theme', 'dark');
  }
}

async function initTheme() {
  const savedTheme = localStorage.getItem('fraudguard_theme');
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    try {
      const res = await fetch('/api/settings');
      const json = await res.json();
      if (json.success && json.data && json.data.appearance_theme) {
        applyTheme(json.data.appearance_theme);
      }
    } catch (e) {}
  }
}

window.applyTheme = applyTheme;

// Dynamic Local Live Clock
function initLiveClock() {
  const clockEl = document.getElementById('live-clock');
  if (!clockEl) return;

  function updateClock() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-US', {
      weekday: 'short',
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
    const timeStr = now.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
    clockEl.innerHTML = `<i class="fa-solid fa-clock" style="margin-right:6px;"></i> ${dateStr} • ${timeStr}`;
  }

  updateClock();
  setInterval(updateClock, 1000);
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'fa-circle-info';
  if (type === 'success') icon = 'fa-circle-check';
  if (type === 'error') icon = 'fa-circle-exclamation';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Right Slide-in SOC Investigation Drawer
async function openInvestigationDrawer(txnId) {
  const overlay = document.getElementById('drawer-overlay');
  const drawer = document.getElementById('investigation-drawer');
  const body = document.getElementById('drawer-body');
  
  if (!overlay || !drawer || !body) return;

  body.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><br><br>Fetching transaction intelligence...</div>`;
  overlay.classList.add('active');
  drawer.classList.add('active');

  try {
    const res = await fetch(`/api/transactions/${txnId}`);
    const json = await res.json();
    
    if (!json.success || !json.data) {
      body.innerHTML = `<div style="color:var(--risk-high);">Transaction record ${txnId} not found.</div>`;
      return;
    }

    const item = json.data;
    const badgeClass = item.risk_level === 'HIGH RISK' ? 'badge-risk-high' : (item.risk_level === 'CHECK' ? 'badge-risk-check' : 'badge-risk-safe');
    const reasons = (item.reasons || []).map(r => `<li style="margin-bottom:6px;">${r}</li>`).join('');

    body.innerHTML = `
      <div style="margin-bottom: 20px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px;">
        <div style="font-size: 1.3rem; font-weight: 800; color: var(--text-main); margin-bottom: 6px;">
          ${item.transaction_id}
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
          <span class="badge-risk ${badgeClass}">${item.risk_level} (${item.risk_score}%)</span>
          <span class="badge-status badge-status-${item.status.toLowerCase()}">${item.status}</span>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; font-size: 0.85rem; background-color: var(--bg-card); padding: 16px; border-radius: 8px; border: 1px solid var(--border-subtle);">
        <div><span style="color:var(--text-muted);">Amount:</span><br><strong style="font-size:1.1rem; color:var(--text-main);">₹${item.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></div>
        <div><span style="color:var(--text-muted);">Method:</span><br><strong style="color:var(--text-main);">${item.payment_method}</strong></div>
        <div><span style="color:var(--text-muted);">Location:</span><br><strong style="color:var(--text-main);">${item.location}</strong> ${item.location_change ? '⚠️' : ''}</div>
        <div><span style="color:var(--text-muted);">Device:</span><br><strong style="color:var(--text-main);">${item.device}</strong> ${item.new_device ? '⚠️' : ''}</div>
        <div><span style="color:var(--text-muted);">Fraud Probability:</span><br><strong style="color:var(--text-main);">${item.fraud_probability}%</strong></div>
        <div><span style="color:var(--text-muted);">Anomaly Pattern:</span><br><strong style="color:var(--text-main);">${item.is_anomaly ? '🔴 Detected' : '🟢 Normal'}</strong></div>
      </div>

      <div style="background-color: var(--bg-card); border: 1px solid var(--border-subtle); padding: 16px; border-radius: 8px; margin-bottom: 24px;">
        <div style="font-weight: 700; font-size: 0.85rem; margin-bottom: 8px; color: var(--cyan-accent);">
          <i class="fa-solid fa-microchip"></i> RISK ENGINE EVIDENCE REASONS:
        </div>
        <ul style="padding-left: 20px; font-size: 0.85rem; color: var(--text-main);">
          ${reasons || '<li>Regular transaction baseline parameters</li>'}
        </ul>
      </div>

      <div style="margin-top: auto; display: flex; flex-direction: column; gap: 10px;">
        <div style="font-weight:700; font-size:0.8rem; color:var(--text-muted); text-transform:uppercase;">Execute Analyst Action:</div>
        <div style="display: flex; gap: 10px;">
          <button class="btn btn-success" style="flex:1;" onclick="drawerTakeAction('${item.transaction_id}', 'ALLOW')">
            <i class="fa-solid fa-check"></i> ALLOW
          </button>
          <button class="btn btn-warning" style="flex:1;" onclick="drawerTakeAction('${item.transaction_id}', 'REVIEW')">
            <i class="fa-solid fa-eye"></i> REVIEW
          </button>
          <button class="btn btn-danger" style="flex:1;" onclick="drawerTakeAction('${item.transaction_id}', 'BLOCK')">
            <i class="fa-solid fa-ban"></i> BLOCK
          </button>
        </div>
      </div>
    `;

  } catch (err) {
    body.innerHTML = `<div style="color:var(--risk-high);">Error opening drawer: ${err.message}</div>`;
  }
}

function closeDrawer() {
  const overlay = document.getElementById('drawer-overlay');
  const drawer = document.getElementById('investigation-drawer');
  if (overlay) overlay.classList.remove('active');
  if (drawer) drawer.classList.remove('active');
}

async function drawerTakeAction(txnId, actionType) {
  try {
    const res = await fetch(`/api/transactions/${txnId}/action`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: actionType})
    });
    const json = await res.json();
    if (json.success) {
      showToast(`Transaction ${txnId} status updated to ${json.data.status}`, 'success');
      closeDrawer();
      if (window.loadTransactionsPage) window.loadTransactionsPage(1);
      if (window.loadSuspiciousList) window.loadSuspiciousList();
      if (window.loadDashboardStats) window.loadDashboardStats();
      if (window.loadRecentPayments) window.loadRecentPayments();
    } else {
      showToast(json.error, 'error');
    }
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function handleGlobalSearch(e) {
  if (e.key === 'Enter') {
    const q = e.target.value.trim();
    if (q) {
      window.location.href = `/transactions?search=${encodeURIComponent(q)}`;
    }
  }
}

// Global modal fallback compatibility
window.openDetailModal = openInvestigationDrawer;
