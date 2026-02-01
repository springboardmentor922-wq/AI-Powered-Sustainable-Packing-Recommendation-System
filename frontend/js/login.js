// ======================================================
// LOGIN PAGE LOGIC
// ======================================================

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://your-backend.onrender.com';

// DOM Elements
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('loginBtn');
const passwordHint = document.getElementById('passwordHint');
const attemptsInfo = document.getElementById('attemptsInfo');
const attemptsText = document.getElementById('attemptsText');
const loginCard = document.getElementById('loginCard');
const deniedCard = document.getElementById('deniedCard');
const registerLink = document.getElementById('registerLink');
const toast = document.getElementById('toast');

// ======================================================
// EVENT LISTENERS
// ======================================================
loginForm.addEventListener('submit', handleLogin);
registerLink.addEventListener('click', handleRegister);
window.addEventListener('DOMContentLoaded', checkAuth);

// ======================================================
// CHECK AUTHENTICATION
// ======================================================
async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/api/auth/status`, {
            credentials: 'include'
        });
        if (response.ok) {
            const data = await response.json();
            if (data.authenticated) {
                window.location.href = 'index.html';
            }
        }
    } catch (error) {
        console.error('Auth check error:', error);
    }
}

// ======================================================
// HANDLE LOGIN
// ======================================================
async function handleLogin(e) {
    e.preventDefault();
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (response.ok) {
            showToast('✅ Login successful!', 'success');
            setTimeout(() => window.location.href = 'index.html', 1000);
        } else if (response.status === 404) {
            showToast('❌ Email not registered. Please register.', 'error');
        } else if (response.status === 403) {
            showAccessDenied();
        } else if (response.status === 401) {
            showToast(data.error || 'Invalid password', 'error');
            passwordInput.classList.add('error');
            if (data.attempts_remaining !== undefined) {
                attemptsInfo.classList.remove('hidden');
                attemptsText.textContent = `⚠️ Invalid password. ${data.attempts_remaining} attempt${data.attempts_remaining !== 1 ? 's' : ''} remaining.`;
            }
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error(error);
        showToast('Network error. Please check if backend is running.', 'error');
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login';
    }
}

// ======================================================
// HANDLE REGISTER
// ======================================================
async function handleRegister(e) {
    e.preventDefault();
    const email = emailInput.value.trim();
    if (!email) {
        showToast('Enter your email first to register', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (res.ok) {
            showToast('✅ Registration created! Please set your password.', 'success');
        } else {
            showToast('❌ ' + (data.error || 'Registration failed'), 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('Network error during registration', 'error');
    }
}

// ======================================================
// SHOW ACCESS DENIED
// ======================================================
function showAccessDenied() {
    loginCard.classList.add('hidden');
    deniedCard.classList.remove('hidden');
}

// ======================================================
// TOAST
// ======================================================
function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 4000);
}

// ======================================================
// INPUT EVENTS
// ======================================================
emailInput.addEventListener('input', () => {
    emailInput.classList.remove('error');
    attemptsInfo.classList.add('hidden');
});

passwordInput.addEventListener('input', () => {
    passwordInput.classList.remove('error');
    attemptsInfo.classList.add('hidden');
});
