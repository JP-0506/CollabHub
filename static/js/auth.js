// ================= MESSAGE HELPERS =================

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


        setTimeout(() => {

            el.style.display = 'none';

            if (callback) callback();

        }, 1500);
    }
}


function clearMessages() {

    document
        .querySelectorAll('.alert-error')
        .forEach(el => el.style.display = 'none');

    document
        .querySelectorAll('.alert-success')
        .forEach(el => el.style.display = 'none');
}


// ================= PASSWORD TOGGLE =================

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


// ================= LOGIN =================

function handleLogin(e) {

    e.preventDefault();

    clearMessages();


    const emailInput = document.getElementById('login-input');

    const passInput = document.getElementById('login-pass');


    const email = emailInput.value.trim();

    const password = passInput.value.trim();


    if (!email || !password) {

        showError('login-error', 'Please fill out all fields');

        return;
    }


    fetch('/auth/login', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            email: email,
            password: password
        })
    })

        .then(res => {

            // 🔐 SAFETY CHECK
            if (!res.ok) {

                throw new Error("Server Error");
            }

            return res.json();
        })

        .then(data => {

            if (data.success) {

                showSuccess('login-success', data.message, () => {

                    window.location.href = data.redirect_url;
                });

            } else {

                showError('login-error', data.message);

                if (data.error_type === 'password') {

                    passInput.value = "";

                    passInput.focus();
                }
            }
        })

        .catch(err => {

            console.error("Login Error:", err);

            showError(
                'login-error',
                'Server error. Please try again.'
            );
        });
}


// ================= SIGNUP =================

function handleSignup(e) {

    e.preventDefault();

    clearMessages();


    const username =
        document.getElementById("signup-name").value.trim();

    const email =
        document.getElementById("signup-email").value.trim();

    const password =
        document.getElementById("signup-pass").value;

    const confirmPassword =
        document.getElementById("signup-confirm").value;


    if (!username || !email || !password || !confirmPassword) {

        showError("signup-error", "All fields are required");

        return;
    }


    if (password.length < 8) {

        showError(
            'signup-error',
            'Password must be at least 8 characters'
        );

        return;
    }


    if (password !== confirmPassword) {

        showError(
            'signup-error',
            'Passwords do not match'
        );

        return;
    }


    fetch("/auth/signup", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            confirm_password: confirmPassword
        })
    })

        .then(res => {

            if (!res.ok) {

                throw new Error("Server Error");
            }

            return res.json();
        })

        .then(data => {

            if (data.success) {

                showSuccess('signup-success', data.message, () => {

                    window.location.href = data.redirect_url;
                });

            } else {

                showError("signup-error", data.message);
            }
        })

        .catch(err => {

            console.error("Signup Error:", err);

            showError(
                "signup-error",
                "Server error. Try again."
            );
        });
}


// ================= RESET =================

function handleReset(e) {

    e.preventDefault();

    alert("Reset link sent!");
}

/*********forgot */
// ================= MESSAGE HELPERS =================

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


        setTimeout(() => {

            el.style.display = 'none';

            if (callback) callback();

        }, 1500);
    }
}


function clearMessages() {

    document
        .querySelectorAll('.alert-error')
        .forEach(el => el.style.display = 'none');

    document
        .querySelectorAll('.alert-success')
        .forEach(el => el.style.display = 'none');
}


// ================= PASSWORD TOGGLE =================

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


// ================= LOGIN =================

function handleLogin(e) {

    e.preventDefault();

    clearMessages();


    const emailInput = document.getElementById('login-input');

    const passInput = document.getElementById('login-pass');


    const email = emailInput.value.trim();

    const password = passInput.value.trim();


    if (!email || !password) {

        showError('login-error', 'Please fill out all fields');

        return;
    }


    fetch('/auth/login', {

        method: 'POST',

        headers: {
            'Content-Type': 'application/json'
        },

        body: JSON.stringify({
            email: email,
            password: password
        })
    })

        .then(res => {

            // 🔐 SAFETY CHECK
            if (!res.ok) {

                throw new Error("Server Error");
            }

            return res.json();
        })

        .then(data => {

            if (data.success) {

                showSuccess('login-success', data.message, () => {

                    window.location.href = data.redirect_url;
                });

            } else {

                showError('login-error', data.message);

                if (data.error_type === 'password') {

                    passInput.value = "";

                    passInput.focus();
                }
            }
        })

        .catch(err => {

            console.error("Login Error:", err);

            showError(
                'login-error',
                'Server error. Please try again.'
            );
        });
}


// ================= SIGNUP =================

function handleSignup(e) {

    e.preventDefault();

    clearMessages();


    const username =
        document.getElementById("signup-name").value.trim();

    const email =
        document.getElementById("signup-email").value.trim();

    const password =
        document.getElementById("signup-pass").value;

    const confirmPassword =
        document.getElementById("signup-confirm").value;


    if (!username || !email || !password || !confirmPassword) {

        showError("signup-error", "All fields are required");

        return;
    }


    if (password.length < 8) {

        showError(
            'signup-error',
            'Password must be at least 8 characters'
        );

        return;
    }


    if (password !== confirmPassword) {

        showError(
            'signup-error',
            'Passwords do not match'
        );

        return;
    }


    fetch("/auth/signup", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            confirm_password: confirmPassword
        })
    })

        .then(res => {

            if (!res.ok) {

                throw new Error("Server Error");
            }

            return res.json();
        })

        .then(data => {

            if (data.success) {

                showSuccess('signup-success', data.message, () => {

                    window.location.href = data.redirect_url;
                });

            } else {

                showError("signup-error", data.message);
            }
        })

        .catch(err => {

            console.error("Signup Error:", err);

            showError(
                "signup-error",
                "Server error. Try again."
            );
        });
}


// ================= FORGOT PASSWORD / OTP =================

// Global variables for OTP functionality
let userEmail = '';
let timeLeft = 30; // 5 minutes
let timerInterval;

function sendOtp(event) {
    event.preventDefault();

    userEmail = document.getElementById('email').value.trim();
    const btn = document.getElementById('sendOtpBtn');

    if (!userEmail) {
        alert('Please enter your email');
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Sending...';

    fetch('/auth/send-otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: userEmail })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show OTP form
                document.getElementById('emailForm').style.display = 'none';
                document.getElementById('otpForm').style.display = 'block';
                document.getElementById('subtitle').textContent = 'Enter OTP';
                document.getElementById('emailDisplay').innerHTML =
                    `OTP sent to: <strong>${userEmail}</strong>`;

                // Start timer
                startTimer();

                // Clear OTP inputs before showing form
                document.querySelectorAll('.otp-input').forEach(input => {
                    input.value = '';
                });

                // Show OTP if in debug mode
                if (data.debug_otp) {
                    alert(`OTP: ${data.debug_otp}`);
                }
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error');
        })
        .finally(() => {
            btn.disabled = false;
            btn.textContent = 'Send OTP';
        });
}

function startTimer() {
    timeLeft = 30;
    updateTimer();

    timerInterval = setInterval(() => {
        timeLeft--;
        updateTimer();

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert('OTP expired! Please request again.');
            goBack();
        }
    }, 1000);
}

function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    document.getElementById('timer').textContent =
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function goBack() {
    clearInterval(timerInterval);

    // Clear all OTP inputs
    document.querySelectorAll('.otp-input').forEach(input => {
        input.value = '';
    });

    document.getElementById('emailForm').style.display = 'block';
    document.getElementById('otpForm').style.display = 'none';
    document.getElementById('subtitle').textContent = 'Enter your email to get OTP';
    document.getElementById('email').value = '';

    // Reset timer variable
    timeLeft = 30;
}

function verifyOtp() {
    // Get OTP from inputs
    const otp =
        document.getElementById('otp1').value +
        document.getElementById('otp2').value +
        document.getElementById('otp3').value +
        document.getElementById('otp4').value +
        document.getElementById('otp5').value +
        document.getElementById('otp6').value;

    if (otp.length !== 6) {
        alert('Please enter complete 6-digit OTP');
        return;
    }

    fetch('/auth/verify-otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: userEmail,
            otp: otp
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('OTP verified! Redirecting to reset password...');
                window.location.href = data.reset_url;
            } else {
                alert(data.message);

                // ✅ YEH LINES ADD KARO - Clear all OTP inputs when wrong
                document.querySelectorAll('.otp-input').forEach(input => {
                    input.value = '';
                });

                // Focus on first OTP input
                document.getElementById('otp1').focus();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error');

            // ✅ ERROR mein bhi clear karo
            document.querySelectorAll('.otp-input').forEach(input => {
                input.value = '';
            });
            document.getElementById('otp1').focus();
        });
}

// Initialize OTP input listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Auto-focus and move between OTP inputs
    document.querySelectorAll('.otp-input').forEach((input, index) => {
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1) {
                const next = document.querySelectorAll('.otp-input')[index + 1];
                if (next) next.focus();
            }
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && e.target.value === '') {
                const prev = document.querySelectorAll('.otp-input')[index - 1];
                if (prev) prev.focus();
            }

            // ✅ ENTER KEY PRESS - Direct verify OTP
            if (e.key === 'Enter') {
                e.preventDefault();  // Form submit roko
                verifyOtp();          // OTP verify karo
            }
        });
    });
});

// ================= RESET PASSWORD =================

// Message functions for reset password page
function showMessage(type, text) {
    const alert = document.getElementById('messageAlert');
    const textElement = document.getElementById('messageText');

    alert.className = `alert alert-${type} alert-dismissible fade show`;
    textElement.textContent = text;
    alert.style.display = 'block';
}

function hideMessage() {
    document.getElementById('messageAlert').style.display = 'none';
}

// Password match validation
function checkPasswordMatch() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');

    if (!password || !confirmPassword) return true;

    const matchElement = document.getElementById('passwordMatch');

    if (password.value && confirmPassword.value) {
        if (password.value === confirmPassword.value) {
            matchElement.textContent = "✓ Passwords match";
            matchElement.style.color = "#28a745";
            return true;
        } else {
            matchElement.textContent = "✗ Passwords do not match";
            matchElement.style.color = "#dc3545";
            return false;
        }
    }
    return true;
}

// Initialize reset password page
function initResetPassword() {
    const passwordField = document.getElementById('password');
    const confirmField = document.getElementById('confirm_password');

    if (passwordField && confirmField) {
        passwordField.addEventListener('input', checkPasswordMatch);
        confirmField.addEventListener('input', checkPasswordMatch);
    }

    const form = document.getElementById('resetPasswordForm');
    if (form) {
        form.addEventListener('submit', handleResetPassword);
    }
}

// Handle reset password form submission
async function handleResetPassword(e) {
    e.preventDefault();

    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const token = document.getElementById('token').value;
    const submitBtn = document.getElementById('submitBtn');
    const buttonText = document.getElementById('buttonText');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Validation
    if (!password || !confirmPassword) {
        showMessage('danger', 'Please fill all fields');
        return;
    }

    if (password.length < 8) {
        showMessage('danger', 'Password must be at least 8 characters');
        return;
    }

    if (password !== confirmPassword) {
        showMessage('danger', 'Passwords do not match');
        return;
    }

    // Show loading
    submitBtn.disabled = true;
    buttonText.textContent = 'Resetting...';
    loadingSpinner.style.display = 'inline-block';

    try {
        const response = await fetch(`/auth/reset-password/${token}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                password: password,
                confirm_password: confirmPassword
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('success', data.message);

            // Redirect to login after 3 seconds
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 3000);
        } else {
            showMessage('danger', data.message);
            submitBtn.disabled = false;
            buttonText.textContent = 'Reset Password';
            loadingSpinner.style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        showMessage('danger', 'Network error. Please try again.');
        submitBtn.disabled = false;
        buttonText.textContent = 'Reset Password';
        loadingSpinner.style.display = 'none';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initResetPassword();
});