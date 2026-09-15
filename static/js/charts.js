/* FRAUDGUARD AI — Chart.js Dark Analytics */

document.addEventListener('DOMContentLoaded', () => {
  initActivityCharts();
});

async function initActivityCharts() {
  try {
    const res = await fetch('/api/activity');
    const json = await res.json();

    if (!json.success || !json.data) return;

    const data = json.data;

    // 1. Risk Distribution Doughnut Chart
    const ctxRisk = document.getElementById('chart-risk-distribution');
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
          plugins: {
            legend: { position: 'bottom', labels: { color: '#94a3b8' } }
          }
        }
      });
    }

    // 2. 7-Day Trend Line Chart
    const ctxTrend = document.getElementById('chart-trend');
    if (ctxTrend) {
      new Chart(ctxTrend.getContext('2d'), {
        type: 'line',
        data: {
          labels: data.trend.dates,
          datasets: [
            {
              label: 'Safe Transactions',
              data: data.trend.safe,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              fill: true,
              tension: 0.3
            },
            {
              label: 'High Risk / Suspicious',
              data: data.trend.suspicious,
              borderColor: '#ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.12)',
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { color: '#94a3b8' } }
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
          }
        }
      });
    }

    // 3. Payment Methods Volume Bar Chart
    const ctxMethods = document.getElementById('chart-methods');
    if (ctxMethods) {
      new Chart(ctxMethods.getContext('2d'), {
        type: 'bar',
        data: {
          labels: data.payment_methods.labels,
          datasets: [{
            label: 'Total Monitored Transactions',
            data: data.payment_methods.data,
            backgroundColor: ['#00f0ff', '#2563eb', '#7c3aed', '#3b82f6'],
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
            y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' }, beginAtZero: true }
          }
        }
      });
    }

  } catch (err) {
    console.error('Error initializing activity charts', err);
  }
}
