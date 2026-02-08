/****************** profile.js ************************/


// =======================
// Profile Page Init
// =======================
document.addEventListener("DOMContentLoaded", function () {

    initPasswordValidation();

});


// =======================
// Password Live Validation
// =======================
function initPasswordValidation() {

    const password = document.getElementById('newPassword');
    const confirmPassword = document.getElementById('confirmPassword');

    if (!password || !confirmPassword) return;

    function validatePasswords() {

        if (password.value !== confirmPassword.value) {

            confirmPassword.setCustomValidity('Passwords do not match');

        } else {

            confirmPassword.setCustomValidity('');
        }
    }

    password.addEventListener('input', validatePasswords);
    confirmPassword.addEventListener('input', validatePasswords);
}
