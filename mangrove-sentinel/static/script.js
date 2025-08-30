// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const links = document.querySelector('.nav-links');
if (toggle) {
  toggle.addEventListener('click', () => {
    links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
  });
}

// Dashboard functionality
document.addEventListener('DOMContentLoaded', async function() {
  // Only run on dashboard page
  if (window.location.pathname === '/dashboard') {
    await loadDashboardData();
  }
});

async function loadDashboardData() {
  try {
    // Load dashboard stats
    const statsResponse = await fetch('/api/v1/dashboard/stats');
    if (statsResponse.ok) {
      const stats = await statsResponse.json();
      updateDashboardStats(stats);
    }

    // Load alerts
    const alertsResponse = await fetch('/api/v1/alerts');
    if (alertsResponse.ok) {
      const alerts = await alertsResponse.json();
      updateAlertsList(alerts);
    }

    // Load impact data and update chart
    const impactResponse = await fetch('/api/v1/dashboard/impact');
    if (impactResponse.ok) {
      const impactData = await impactResponse.json();
      updateImpactChart(impactData);
    }

  } catch (error) {
    console.error('Error loading dashboard data:', error);
  }
}

function updateDashboardStats(stats) {
  const activeAlerts = document.getElementById('active-alerts');
  const highRiskZones = document.getElementById('high-risk-zones');
  const validatedReports = document.getElementById('validated-reports');
  const communitySentinels = document.getElementById('community-sentinels');

  if (activeAlerts) activeAlerts.textContent = stats.active_alerts;
  if (highRiskZones) highRiskZones.textContent = stats.high_risk_zones;
  if (validatedReports) validatedReports.textContent = stats.validated_reports.toLocaleString();
  if (communitySentinels) communitySentinels.textContent = stats.community_sentinels.toLocaleString();
}

function updateAlertsList(alerts) {
  const alertsList = document.getElementById('alerts-list');
  if (!alertsList) return;

  alertsList.innerHTML = '';
  
  alerts.slice(0, 4).forEach(alert => {
    const li = document.createElement('li');
    const dotClass = getSeverityDotClass(alert.severity);
    li.innerHTML = `<span class="dot ${dotClass}"></span> ${alert.title}`;
    alertsList.appendChild(li);
  });
}

function getSeverityDotClass(severity) {
  switch (severity) {
    case 'high': return 'dot-red';
    case 'medium': return 'dot-amber';
    case 'low': return 'dot-green';
    default: return 'dot-amber';
  }
}

function updateImpactChart(impactData) {
  const ctx = document.getElementById('impactChart');
  if (!ctx) return;

  // Clear existing chart if it exists
  if (window.impactChart) {
    window.impactChart.destroy();
  }

  const labels = impactData.map(item => item.month);
  const data = impactData.map(item => item.validated_reports);

  window.impactChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Validated Reports',
        data: data,
        fill: false,
        borderColor: '#22c55e',
        backgroundColor: '#22c55e',
        borderWidth: 2,
        tension: 0.35,
        pointBackgroundColor: '#22c55e',
        pointBorderColor: '#22c55e'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: false } 
      },
      scales: {
        x: { 
          grid: { display: false }, 
          ticks: { color: '#bdbdbd' } 
        },
        y: { 
          grid: { color: 'rgba(255,255,255,0.08)' }, 
          ticks: { color: '#bdbdbd' } 
        }
      }
    }
  });
}

// Sentinel registration form (can be added to index page)
async function registerSentinel(formData) {
  try {
    const response = await fetch('/api/sentinels', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      const result = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Success!', 'Successfully registered as a Sentinel!', 'success');
      }
      return result;
    } else {
      const error = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Registration Failed', error.detail, 'error');
      }
    }
  } catch (error) {
    console.error('Registration error:', error);
    if (typeof showToast !== 'undefined') {
      showToast('Error', 'Registration failed. Please try again.', 'error');
    }
  }
}

// Report submission (legacy - use authenticated version)
async function submitReport(reportData) {
  try {
    const response = await fetch('/api/reports', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reportData)
    });

    if (response.ok) {
      const result = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Success!', 'Report submitted successfully!', 'success');
      }
      return result;
    } else {
      const error = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Submission Failed', error.detail, 'error');
      }
    }
  } catch (error) {
    console.error('Report submission error:', error);
    if (typeof showToast !== 'undefined') {
      showToast('Error', 'Report submission failed. Please try again.', 'error');
    }
  }
}

// Authenticated report submission
async function submitAuthenticatedReport(reportData) {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/reports', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(reportData)
    });

    if (response.ok) {
      const result = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Success!', 'Report submitted successfully!', 'success');
      }
      return result;
    } else {
      const error = await response.json();
      if (typeof showToast !== 'undefined') {
        showToast('Submission Failed', error.detail, 'error');
      }
    }
  } catch (error) {
    console.error('Report submission error:', error);
    if (typeof showToast !== 'undefined') {
      showToast('Error', 'Report submission failed. Please try again.', 'error');
    }
  }
}
