

function switchMode(mode) {
    const title = document.getElementById('auth-title');
    const subtitle = document.getElementById('auth-subtitle');
    const nameRow = document.getElementById('name-row');
    const termsBox = document.getElementById('terms-box');
    const submitBtn = document.getElementById('main-auth-btn');

    if (mode === 'signin') {
        title.innerText = "Welcome back";
        subtitle.innerHTML = 'New here? <a href="#" onclick="switchMode(\'signup\')">Create an account</a>';
        nameRow.style.display = "none";
        termsBox.style.display = "none";
        submitBtn.innerText = "Log in";
    } else {
        title.innerText = "Create an account";
        subtitle.innerHTML = 'Already have an account? <a href="#" onclick="switchMode(\'signin\')">Log in</a>';
        nameRow.style.display = "flex";
        termsBox.style.display = "flex";
        submitBtn.innerText = "Create account";
    }
}

// Close modal when clicking background
window.onclick = function (event) {
    if (event.target == document.getElementById('authModal')) closeModal();

}
