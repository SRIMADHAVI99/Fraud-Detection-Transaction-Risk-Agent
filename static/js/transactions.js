/* FRAUDGUARD AI — Transactions Page JS */

let currentPage = 1;
let searchTimer = null;

document.addEventListener('DOMContentLoaded', () => {
  // Read search query param from URL if redirected from global search
  const urlParams = new URLSearchParams(window.location.search);
  const q = urlParams.get('search');
  if (q) {
    const searchInput = document.getElementById('filter-search');
    if (searchInput) searchInput.value = q;
  }
  loadTransactionsPage(1);
});

function debounceSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    loadTransactionsPage(1);
  }, 350);
}

async function loadTransactionsPage(page = 1) {
  currentPage = page;
  const tbody = document.getElementById('transactions-table-body');
  const info = document.getElementById('pagination-info');
  const prevBtn = document.getElementById('btn-prev-page');
  const nextBtn = document.getElementById('btn-next-page');

  if (!tbody) return;

  const search = document.getElementById('filter-search').value.trim();
  const risk = document.getElementById('filter-risk').value;
  const method = document.getElementById('filter-method').value;
  const status = document.getElementById('filter-status').value;

  tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 24px; color: var(--text-muted);"><i class="fa-solid fa-spinner fa-spin"></i> Loading transactions...</td></tr>`;

  try {
    const url = `/api/transactions?page=${page}&per_page=15&search=${encodeURIComponent(search)}&risk_level=${encodeURIComponent(risk)}&payment_method=${encodeURIComponent(method)}&status=${encodeURIComponent(status)}`;
    const res = await fetch(url);
    const json = await res.json();

    if (!json.success || !json.data.items.length) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 24px; color: var(--text-muted);">No matching transactions found.</td></tr>`;
      if (info) info.textContent = `Page 0 of 0 (0 items)`;
      if (prevBtn) prevBtn.disabled = true;
      if (nextBtn) nextBtn.disabled = true;
      return;
    }

    const data = json.data;
    if (info) info.textContent = `Showing page ${data.current_page} of ${data.pages} (${data.total.toLocaleString()} total items)`;
    
    if (prevBtn) prevBtn.disabled = data.current_page <= 1;
    if (nextBtn) nextBtn.disabled = data.current_page >= data.pages;

    tbody.innerHTML = data.items.map(item => {
      let badgeClass = 'badge-risk-safe';
      if (item.risk_level === 'CHECK') badgeClass = 'badge-risk-check';
      if (item.risk_level === 'HIGH RISK') badgeClass = 'badge-risk-high';

      return `
        <tr onclick="openInvestigationDrawer('${item.transaction_id}')">
          <td><strong>${item.transaction_id}</strong></td>
          <td>₹${item.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
          <td>${item.location}</td>
          <td>${item.device}</td>
          <td>${item.payment_method}</td>
          <td>${item.risk_score}%</td>
          <td><span class="badge-risk ${badgeClass}">${item.risk_level}</span></td>
          <td><span class="badge-status badge-status-${item.status.toLowerCase()}">${item.status}</span></td>
          <td>${item.created_at ? item.created_at.split(' ')[0] : 'Today'}</td>
        </tr>
      `;
    }).join('');

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" style="color:var(--risk-high); text-align:center;">Failed to load transactions: ${err.message}</td></tr>`;
  }
}

function changePage(delta) {
  loadTransactionsPage(currentPage + delta);
}

window.loadTransactionsPage = loadTransactionsPage;
