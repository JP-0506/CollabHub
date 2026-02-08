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
