// ===== ADMIN PROFILE PAGE JS =====

// Profile Completion
(function () {
    const name = document.getElementById('view_name')?.textContent.trim();
    const email = document.getElementById('view_email')?.textContent.trim();
    let pct = 0;
    if (name && name !== '—') pct += 50;
    if (email && email !== '—') pct += 50;
    document.getElementById('completionPct').textContent = pct + '%';
    document.getElementById('completionBar').style.width = pct + '%';
})();


// Toggle Edit Mode
function toggleEditMode() {
    const card = document.getElementById('profileFormCard');
    card.classList.toggle('edit-mode');
    const isEdit = card.classList.contains('edit-mode');
    document.getElementById('editToggleBtn').innerHTML = isEdit
        ? '<i class="fas fa-times me-2"></i>Cancel Edit'
        : '<i class="fas fa-edit me-2"></i>Edit Profile';
    document.getElementById('editModeBadge').style.display = isEdit ? 'inline-block' : 'none';
}

function cancelEdit() {
    const card = document.getElementById('profileFormCard');
    card.classList.remove('edit-mode');
    document.getElementById('editToggleBtn').innerHTML = '<i class="fas fa-edit me-2"></i>Edit Profile';
    document.getElementById('editModeBadge').style.display = 'none';
}


// Save Profile
async function saveProfile() {
    const form = document.getElementById('profileUpdateForm');
    const msgDiv = document.getElementById('profileMsg');
    const formData = new FormData(form);

    const res = await fetch(window.location.href, { method: 'POST', body: formData });
    const data = await res.json();

    msgDiv.style.display = 'block';
    if (data.status === 'success') {
        msgDiv.className = 'alert alert-success';
        msgDiv.textContent = data.message;
        cancelEdit();
        setTimeout(() => location.reload(), 800);
    } else {
        msgDiv.className = 'alert alert-danger';
        msgDiv.textContent = data.message;
    }
}


// Change Password
async function changePassword(e) {
    e.preventDefault();
    const current = document.getElementById('current_password').value;
    const newPw = document.getElementById('new_password').value;
    const confirm = document.getElementById('confirm_password').value;
    const msgDiv = document.getElementById('passwordMsg');

    msgDiv.style.display = 'block';

    if (newPw.length < 8) {
        msgDiv.className = 'alert alert-danger';
        msgDiv.textContent = 'Password must be at least 8 characters.';
        return;
    }
    if (newPw !== confirm) {
        msgDiv.className = 'alert alert-danger';
        msgDiv.textContent = 'Passwords do not match.';
        return;
    }

    const res = await fetch('/admin/change_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: current, new_password: newPw })
    });
    const data = await res.json();

    if (data.status === 'success') {
        msgDiv.className = 'alert alert-success';
        msgDiv.textContent = data.message;
        document.getElementById('passwordForm').reset();
    } else {
        msgDiv.className = 'alert alert-danger';
        msgDiv.textContent = data.message;
    }
}