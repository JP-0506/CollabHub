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

        // 1.5 સેકન્ડ પછી મેસેજ ગાયબ થશે
        setTimeout(() => {
            el.style.display = 'none';
            if (callback) callback();
        }, 1500);
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

// --- FORM HANDLERS (USING .then() INSTEAD OF ASYNC/AWAIT) ---

function handleLogin(e) {
    e.preventDefault(); // પેજ રિલોડ થતું અટકાવશે
    clearMessages();

    const emailInput = document.getElementById('login-input');
    const passInput = document.getElementById('login-pass');

    const email = emailInput.value.trim();
    const password = passInput.value.trim();

    // 1. ખાલી ફોર્મ ચેક કરો
    if (!email || !password) {
        showError('login-error', 'Please fill out all fields');
        return;
    }

    // 2. ડેટા મોકલો (Fetch with .then)
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
        .then(response => response.json()) // સર્વરનો જવાબ JSON માં ફેરવો
        .then(data => {
            // અહીં ડેટા મળી જશે
            if (data.success) {
                // સફળ થાય તો
                showSuccess('login-success', data.message, () => {
                    window.location.href = data.redirect_url;
                });
            } else {
                // એરર આવે તો
                showError('login-error', data.message);

                // જો પાસવર્ડ ખોટો હોય તો જ ફીલ્ડ ખાલી કરો
                if (data.error_type === 'password') {
                    passInput.value = "";
                    passInput.focus();
                }
            }
        })
        .catch(error => {
            // જો સર્વર બંધ હોય કે નેટવર્ક પ્રોબ્લેમ હોય
            console.error('Error:', error);
            showError('login-error', 'Something went wrong. Please try again.');
        });
}

//GEMINI
// function handleSignup(e) {
//     function handleSignup(e) {
//         e.preventDefault();
//         clearMessages();

//         // 1. Get Values
//         const nameInput = document.getElementById('signup-name'); // Full Name (Not used in logic but sent)
//         const emailInput = document.getElementById('signup-email');
//         const passInput = document.getElementById('signup-pass');
//         const confirmInput = document.getElementById('signup-confirm');

//         const name = nameInput.value.trim();
//         const email = emailInput.value.trim();
//         const password = passInput.value.trim();
//         const confirmPass = confirmInput.value.trim();

//         // 2. Validation
//         if (!name || !email || !password || !confirmPass) {
//             showError('signup-error', 'Please fill all fields');
//             return;
//         }

//         if (password !== confirmPass) {
//             showError('signup-error', 'Passwords do not match');
//             passInput.value = "";
//             confirmInput.value = "";
//             return;
//         }

//         if (password.length < 8) {
//             showError('signup-error', 'Password must be at least 8 characters');
//             return;
//         }

//         // 3. Send Data to Backend
//         fetch('/auth/signup', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({
//                 fullname: name,
//                 email: email,
//                 password: password
//             })
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.success) {
//                     // Success Message
//                     showSuccess('signup-success', data.message, () => {
//                         // Redirect to Login Page after success
//                         window.location.href = data.redirect_url;
//                     });
//                 } else {
//                     // Error Message
//                     showError('signup-error', data.message);
//                 }
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//                 showError('signup-error', 'Server Error. Try again.');
//             });
//     }
// }

// //2.CHATGPT
function handleSignup(e) {
    e.preventDefault();
    clearMessages();

    const username = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-pass").value;
    const confirmPassword = document.getElementById("signup-confirm").value;

    // Empty check
    if (!username || !email || !password || !confirmPassword) {
        showError("signup-error", "All fields are required");
        return;
    }

    // Password length
    if (password.length < 8) {
        showError('signup-error', 'Password must be at least 8 characters');
        return;
    }


    // Match check
    if (password !== confirmPassword) {
        showError('signup-error', 'Passwords do not match');
        return;
    }

    // Send to Flask
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
        .then(res => res.json())

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
            console.error(err);
            showError("signup-error", "Server error. Try again.");
        });
}

// function handleReset(e) {
//     e.preventDefault();
//     alert("Reset link sent!");
//     // Logic to close overlay or redirect
// }