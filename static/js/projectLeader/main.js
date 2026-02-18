// Switch Navigation - For Single Page Apps
function switchNav(id, el = null) {
    document.querySelectorAll('.section-view').forEach(v => v.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    if (el) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    }
}

// Initialize tooltips for collapsed sidebar
document.addEventListener('DOMContentLoaded', function () {
    // Initialize dropdowns and other Bootstrap components
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            const dropdownMenu = this.nextElementSibling;
            dropdownMenu.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.matches('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});
function downloadPDF() {
    window.location.href = "{{ url_for('project_leader.export_pdf') }}";
}

function downloadCSV() {
    window.location.href = "{{ url_for('project_leader.export_csv') }}";
}

function sendReportEmail() {
    const form = document.getElementById('emailReportForm');
    const formData = new FormData(form);
    
    fetch("{{ url_for('project_leader.email_report') }}", {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Report sent successfully!');
            bootstrap.Modal.getInstance(document.getElementById('emailModal')).hide();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error sending email: ' + error);
    });
}

// Make sure this runs after the page loads
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('emailReportForm');
    
    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault(); // THIS STOPS PAGE RELOAD
            
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading
            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sending...';
            
            // Send AJAX
            fetch("{{ url_for('project_leader.email_report') }}", {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Report sent successfully!');
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('emailModal'));
                    if (modal) modal.hide();
                    form.reset();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error);
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
            
            return false; // Extra safety to prevent page reload
        };
    }
});
let editMode = false;

function toggleEditMode() {
    editMode = !editMode;
    const form = document.getElementById('profileForm');
    const btn = document.getElementById('editToggleBtn');
    const badge = document.getElementById('editModeBadge');
    
    if (editMode) {
        form.classList.add('edit-mode');
        btn.innerHTML = '<i class="fas fa-times me-2"></i>Cancel Editing';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-secondary');
        badge.style.display = 'inline-block';
    } else {
        form.classList.remove('edit-mode');
        btn.innerHTML = '<i class="fas fa-edit me-2"></i>Edit Profile';
        btn.classList.remove('btn-outline-secondary');
        btn.classList.add('btn-primary');
        badge.style.display = 'none';
    }
}

function enableEdit(field) {
    if (!editMode) {
        toggleEditMode();
    }
    // Optional: Focus on the corresponding input
    const input = document.querySelector(`[name="${field}"]`);
    if (input) input.focus();
}

function cancelEdit() {
    toggleEditMode();
    // Reset form to original values
    location.reload(); // Simple solution - reload to get original data
}

function saveProfile() {
    const form = document.getElementById('profileUpdateForm');
    const formData = new FormData(form);
    
    fetch('/projectleader/update_profile', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Profile updated successfully!');
            location.reload(); // Refresh to show updated data
        } else {
            alert('❌ Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('❌ Error: ' + error);
    });
}

function changePassword(event) {
    event.preventDefault();
    
    const current = document.getElementById('current_password').value;
    const newPass = document.getElementById('new_password').value;
    const confirm = document.getElementById('confirm_password').value;
    
    if (newPass !== confirm) {
        alert('❌ New passwords do not match');
        return;
    }
    
    if (newPass.length < 6) {
        alert('❌ Password must be at least 6 characters');
        return;
    }
    
    const formData = new FormData();
    formData.append('current_password', current);
    formData.append('new_password', newPass);
    formData.append('confirm_password', confirm);
    
    fetch('/projectleader/change_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Password changed successfully!');
            document.getElementById('passwordForm').reset();
        } else {
            alert('❌ Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('❌ Error: ' + error);
    });
}

// Optional: Photo upload handling
document.getElementById('photoUpload').addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('photo', file);
        
        // You'll need to create an upload_photo endpoint
        fetch('/projectleader/upload_photo', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Photo updated!');
                location.reload();
            }
        });
    }
});
function filterTasks() {
    let input = document.getElementById('searchTasks');
    let filter = input.value.toUpperCase();
    let table = document.getElementById('tasksTable');
    let tr = table.getElementsByTagName('tr');
    
    for (let i = 1; i < tr.length; i++) {
        let tdArray = tr[i].getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < tdArray.length - 1; j++) {
            if (tdArray[j]) {
                let textValue = tdArray[j].textContent || tdArray[j].innerText;
                if (textValue.toUpperCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
        }
        
        if (found) {
            tr[i].style.display = '';
        } else {
            tr[i].style.display = 'none';
        }
    }
}

// Edit task function
function editTask(taskId) {
    fetch(`/projectleader/get_task/${taskId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('edit_title').value = data.title;
            document.getElementById('edit_description').value = data.description || '';
            document.getElementById('edit_assigned_to').value = data.assigned_to;
            document.getElementById('edit_project_id').value = data.project_id;
            document.getElementById('edit_priority').value = data.priority;
            document.getElementById('edit_status').value = data.status;
            document.getElementById('edit_due_date').value = data.due_date;
            
            document.getElementById('editTaskForm').action = `/projectleader/update_task/${taskId}`;
            
            let editModal = new bootstrap.Modal(document.getElementById('editTaskModal'));
            editModal.show();
        })
        .catch(error => {
            alert('Error loading task details');
            console.error(error);
        });
}

// Delete task function
function deleteTask(taskId, taskName) {
    document.getElementById('deleteTaskName').textContent = taskName;
    document.getElementById('deleteTaskForm').action = `/projectleader/delete_task/${taskId}`;
    
    let deleteModal = new bootstrap.Modal(document.getElementById('deleteTaskModal'));
    deleteModal.show();
}