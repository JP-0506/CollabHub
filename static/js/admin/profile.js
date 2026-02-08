/****************** profile ************************/


// Initialize Profile Section (Runs after fetch load)
function initProfile() {

    loadSavedProfile();

    initPasswordValidation();
}


// Update Profile
function updateProfile() {

    const fullName = document.getElementById('fullName')?.value || '';
    const email = document.getElementById('email')?.value || '';
    const phone = document.getElementById('phone')?.value || '';
    const bio = document.getElementById('bio')?.value || '';

    // Save to localStorage (Temporary - later replace with backend API)
    localStorage.setItem('adminProfile', JSON.stringify({
        fullName: fullName,
        email: email,
        phone: phone,
        bio: bio,
        lastUpdated: new Date().toISOString()
    }));

    alert('Profile updated successfully!');

    return false; // Prevent form submit
}


// Change Password
function changePassword() {

    const currentPassword =
        document.getElementById('currentPassword')?.value || '';

    const newPassword =
        document.getElementById('newPassword')?.value || '';

    const confirmPassword =
        document.getElementById('confirmPassword')?.value || '';


    // Validation
    if (newPassword.length < 6 || newPassword.length > 12) {

        alert('Password must be 6 to 12 characters');

        return false;
    }

    if (newPassword !== confirmPassword) {

        alert('New password and confirm password do not match');

        return false;
    }

    // Save (Temporary)
    localStorage.setItem('adminPassword', btoa(newPassword));

    alert('Password changed successfully!');

    const form = document.getElementById('passwordForm');

    if (form) {
        form.reset();
    }

    return false;
}


// Load Saved Profile
function loadSavedProfile() {

    const savedProfile = localStorage.getItem('adminProfile');

    if (!savedProfile) return;

    try {

        const profile = JSON.parse(savedProfile);

        const fullName = document.getElementById('fullName');
        const email = document.getElementById('email');
        const phone = document.getElementById('phone');
        const bio = document.getElementById('bio');

        if (fullName) fullName.value = profile.fullName || 'Admin User';

        if (email) email.value = profile.email || 'admin@collabhub.com';

        if (phone) phone.value = profile.phone || '+1 (555) 123-4567';

        if (bio) bio.value = profile.bio || '';

    } catch (error) {

        console.error("Profile load error:", error);
    }
}


// Password Live Validation
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
