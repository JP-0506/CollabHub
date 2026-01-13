function toggleForm(type) {
    const signup = document.getElementById('signup-section');
    const login = document.getElementById('login-section');
    const forgot = document.getElementById('forgot-section');

    // Hide all first
    signup.style.display = 'none';
    login.style.display = 'none';
    forgot.style.display = 'none';

    // Show the requested one
    if (type === 'signup') signup.style.display = 'block';
    if (type === 'login') login.style.display = 'block';
    if (type === 'forgot') forgot.style.display = 'block';
}

function viewPassword(id) {
    const input = document.getElementById(id);
    const icon = input.nextElementSibling;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        input.type = "password";
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    }
}