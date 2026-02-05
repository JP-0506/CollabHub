function updateProfile() {
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const bio = document.getElementById('bio').value;
    
    // Save to localStorage (from syllabus Unit-10)
    localStorage.setItem('adminProfile', JSON.stringify({
        fullName: fullName,
        email: email,
        phone: phone,
        bio: bio,
        lastUpdated: new Date().toISOString()
    }));
    
    alert('Profile updated successfully!');
    return false; // Prevent form submission for demo
}

function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validation from syllabus Unit-10
    if (newPassword.length < 6 || newPassword.length > 12) {
        alert('Password must be 6 to 12 characters');
        return false;
    }
    
    if (newPassword !== confirmPassword) {
        alert('New password and confirm password do not match');
        return false;
    }
    
    // Save to localStorage
    localStorage.setItem('adminPassword', btoa(newPassword));
    
    alert('Password changed successfully!');
    document.getElementById('passwordForm').reset();
    return false;
}

// Load saved profile on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedProfile = localStorage.getItem('adminProfile');
    if (savedProfile) {
        const profile = JSON.parse(savedProfile);
        document.getElementById('fullName').value = profile.fullName || 'Admin User';
        document.getElementById('email').value = profile.email || 'admin@collabhub.com';
        document.getElementById('phone').value = profile.phone || '+1 (555) 123-4567';
        document.getElementById('bio').value = profile.bio || '';
    }
});