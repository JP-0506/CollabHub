// --- MESSAGE HELPERS ---
function showError(id, msg) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = msg;
        el.style.display = 'block';
    }
}

function showSuccess(id, msg, callback) {
    const el = document.getElementById(id);
    if (el) {
        el.innerText = msg;
        el.style.display = 'block';

        // Wait 2 seconds, then execute callback
        setTimeout(() => {
            el.style.display = 'none';
            if (callback) callback();
        }, 2000);
    }
}

function clearMessages() {
    document.querySelectorAll('.alert-error').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.alert-success').forEach(el => el.style.display = 'none');
}

// --- PASSWORD TOGGLE LOGIC ---
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    const len = input.value.length;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }
    input.focus();
    input.setSelectionRange(len, len);
}

// --- FORM HANDLERS ---
function handleLogin(e) {
    e.preventDefault();
    clearMessages();
    const input = document.getElementById('login-input').value;
    const pass = document.getElementById('login-pass').value;

    // Demo logic: Accept 'admin' or 'admin@example.com' with password '123'
    if ((input === 'admin' || input === 'admin@example.com') && pass === '123') {
        showSuccess('login-success', 'Login Successful! Redirecting...', () => {
            // REDIRECT TO HOME PAGE
            window.location.href = '../home.html';
        });
    } else {
        showError('login-error', 'Invalid credentials!');
        document.getElementById('login-pass').value = '';
    }
}

function handleSignup(e) {
    e.preventDefault();
    clearMessages();
    const pass = document.getElementById('signup-pass').value;
    // Renamed variable to avoid conflict with window.confirm()
    const confirmPassword = document.getElementById('signup-confirm').value;

    // 1. CHECK PASSWORD LENGTH (Must be 8+)
    if (pass.length < 8) {
        showError('signup-error', 'Password must be at least 8 characters long!');
        return;
    }

    // 2. CHECK MATCH
    if (pass !== confirmPassword) {
        showError('signup-error', 'Passwords do not match!');
        document.getElementById('signup-confirm').value = '';
        return;
    }

    // 3. SUCCESS
    showSuccess('signup-success', 'Account Created Successfully! Redirecting...', () => {
        // REDIRECT TO HOME PAGE
        window.location.href = '../home.html';
    });
}

function handleReset(e) {
    e.preventDefault();
    alert("Reset link sent!");
    window.location.href = 'login.html';
}