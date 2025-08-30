// Toast notification system
function createToastContainer() {
    if (document.querySelector('.toast-container')) return;
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
}

function showToast(title, message, type = 'info') {
    createToastContainer();
    const container = document.querySelector('.toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <p class="toast-message">${message}</p>
    `;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);
    
    // Remove toast after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

// Authentication utilities
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_data', ''); // Clear old user data
}

function removeToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
}

function getAuthHeaders() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

// User authentication functions
async function registerUser(userData) {
    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            const result = await response.json();
            showToast('Success!', 'Registration successful! You can now login.', 'success');
            return result;
        } else {
            const error = await response.json();
            showToast('Registration Failed', error.detail, 'error');
            return null;
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Error', 'Registration failed. Please try again.', 'error');
        return null;
    }
}

async function loginUser(loginData) {
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        if (response.ok) {
            const result = await response.json();
            setToken(result.access_token);
            showToast('Welcome!', 'Login successful!', 'success');
            return result;
        } else {
            const error = await response.json();
            showToast('Login Failed', error.detail, 'error');
            return null;
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Error', 'Login failed. Please try again.', 'error');
        return null;
    }
}

async function getCurrentUser() {
    try {
        const response = await fetch('/api/v1/auth/me', {
            method: 'GET',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            return await response.json();
        } else {
            console.error('Failed to get current user');
            return null;
        }
    } catch (error) {
        console.error('Get user error:', error);
        return null;
    }
}

async function updateUserProfile(updateData) {
    try {
        const response = await fetch('/api/v1/users/profile', {
            method: 'PUT',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        if (response.ok) {
            const result = await response.json();
            showToast('Updated!', 'Profile updated successfully!', 'success');
            return result;
        } else {
            const error = await response.json();
            showToast('Update Failed', error.detail, 'error');
            return null;
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showToast('Error', 'Profile update failed. Please try again.', 'error');
        return null;
    }
}

async function loadUserProfile() {
    const user = await getCurrentUser();
    if (user) {
        document.getElementById('full_name').value = user.full_name || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('phone').value = user.phone || '';
        document.getElementById('location').value = user.location || '';
        
        document.getElementById('user-points').textContent = user.points || 0;
        document.getElementById('user-status').textContent = user.is_sentinel ? 'Active Sentinel' : 'Member';
        document.getElementById('member-since').textContent = new Date(user.created_at).toLocaleDateString();
    }
}

async function loadUserReports() {
    try {
        const response = await fetch('/api/v1/reports/user/my-reports', {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const reports = await response.json();
            const container = document.getElementById('user-reports-list');
            document.getElementById('user-reports').textContent = reports.length;
            
            if (reports.length === 0) {
                container.innerHTML = '<p class="muted">No reports submitted yet.</p>';
                return;
            }

            container.innerHTML = reports.map(report => `
                <div class="card" style="margin-bottom: 12px; padding: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0 0 4px 0;">${report.title}</h4>
                            <p style="margin: 0; color: var(--muted); font-size: 14px;">${report.location}</p>
                            <p style="margin: 4px 0 0 0; font-size: 14px;">
                                <span class="dot ${getSeverityDotClass(report.severity)}"></span>
                                ${report.threat_type} - ${report.severity}
                            </p>
                        </div>
                        <div>
                            <span class="pill" style="padding: 4px 8px; font-size: 12px; border-radius: 12px; background: ${report.validated ? 'var(--green)' : 'var(--line)'};">
                                ${report.status}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading user reports:', error);
    }
}

function logout() {
    removeToken();
    showToast('Goodbye!', 'Logged out successfully!', 'success');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Check if user is authenticated
function isAuthenticated() {
    return !!getToken();
}

// Redirect to login if not authenticated
function requireAuth() {
    if (!isAuthenticated()) {
        showToast('Login Required', 'Please login to access this page.', 'info');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1500);
        return false;
    }
    return true;
}

// Update navigation based on auth state
async function updateNavigation() {
    const navActions = document.querySelector('.nav-actions');
    if (!navActions) return;
    
    if (isAuthenticated()) {
        const user = await getCurrentUser();
        if (user) {
            navActions.innerHTML = `
                <div class="nav-user-info">
                    <span>Welcome, <span class="nav-user-name">${user.full_name}</span></span>
                </div>
                <a class="btn btn-white" href="/profile">Profile</a>
                <a class="btn btn-green" onclick="logout()">Logout</a>
            `;
        }
    } else {
        // Update for unauthenticated users - show login/register
        const currentPath = window.location.pathname;
        if (currentPath === '/login') {
            navActions.innerHTML = `
                <a class="btn btn-white" href="/register">Register</a>
                <a class="btn btn-green" href="/">Back to Site</a>
            `;
        } else if (currentPath === '/register') {
            navActions.innerHTML = `
                <a class="btn btn-white" href="/login">Login</a>
                <a class="btn btn-green" href="/">Back to Site</a>
            `;
        } else {
            navActions.innerHTML = `
                <a class="btn btn-white" href="/register">Sign up as Sentinel</a>
                <a class="btn btn-green" href="/login">Login</a>
            `;
        }
    }
}

// Initialize authentication state on page load
document.addEventListener('DOMContentLoaded', async function() {
    await updateNavigation();
});

// Helper function for severity dots (reused from script.js)
function getSeverityDotClass(severity) {
    switch (severity) {
        case 'high': return 'dot-red';
        case 'medium': return 'dot-amber';
        case 'low': return 'dot-green';
        default: return 'dot-amber';
    }
}