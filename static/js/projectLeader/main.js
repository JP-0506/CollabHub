console.log("MAIN JS LOADED");

// ========== GLOBAL VARIABLES ==========
let editMode = false;
let currentTaskId = null;
let currentMemberId = null;
let currentMemberName = '';

// ========== SIDEBAR NAVIGATION ==========
function switchNav(id, el = null) {
    document.querySelectorAll('.section-view').forEach(v => v.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    if (el) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    }
}

// ========== DASHBOARD / REPORTS ==========
function downloadPDF() {
    window.location.href = "/projectleader/export_pdf";
}

function downloadCSV() {
    window.location.href = "/projectleader/export_csv";
}

function sendReportEmail() {
    const form = document.getElementById('emailReportForm');
    const formData = new FormData(form);

    fetch("/projectleader/email_report", {
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

// ========== TASKS PAGE ==========
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

function editTask(taskId) {
    fetch(`/projectleader/get_task/${taskId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('edit_title').value = data.title;
            document.getElementById('edit_description').value = data.description || '';
            document.getElementById('edit_assigned_to').value = data.assigned_to;
            document.getElementById('edit_project_id').value = data.project_id;
            document.getElementById('edit_priority').value = data.priority;
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

function deleteTask(taskId, taskName) {
    document.getElementById('deleteTaskName').textContent = taskName;
    document.getElementById('deleteTaskForm').action = `/projectleader/delete_task/${taskId}`;

    let deleteModal = new bootstrap.Modal(document.getElementById('deleteTaskModal'));
    deleteModal.show();
}

// ========== MY TEAM PAGE ==========
function filterTeam() {
    let input = document.getElementById('teamSearch');
    let filter = input.value.toUpperCase();
    let table = document.getElementById('teamTable');
    let tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName('td')[0];
        if (td) {
            let txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = '';
            } else {
                tr[i].style.display = 'none';
            }
        }
    }
}

function filterTeamTable() {
    let input = document.getElementById('tableSearch');
    let filter = input.value.toUpperCase();
    let table = document.getElementById('teamTable');
    let tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName('td')[0];
        if (td) {
            let txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = '';
            } else {
                tr[i].style.display = 'none';
            }
        }
    }
}

function filterByRole() {
    let roleFilter = document.getElementById('roleFilter').value.toLowerCase();
    let table = document.getElementById('teamTable');
    let tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        let roleCell = tr[i].getElementsByTagName('td')[1];
        if (roleCell) {
            let role = roleCell.textContent || roleCell.innerText;
            if (roleFilter === '' || role.toLowerCase().includes(roleFilter)) {
                tr[i].style.display = '';
            } else {
                tr[i].style.display = 'none';
            }
        }
    }
}

function messageMember(userId) {
    currentMemberId = userId;
    let modal = new bootstrap.Modal(document.getElementById('messageModal'));
    modal.show();
}

function viewMemberTasks(userId) {
    window.location.href = "/projectleader/tasks?user=" + userId;
}

function removeMember(userId, memberName) {
    document.getElementById('removeUserId').value = userId;
    document.getElementById('removeMemberName').textContent = memberName;
    let modal = new bootstrap.Modal(document.getElementById('removeMemberModal'));
    modal.show();
}

function openMemberOverview(memberId) {
    fetch(`/projectleader/member_overview/${memberId}`)
        .then(response => {
            if (!response.ok) throw new Error("Server error");
            return response.json();
        })
        .then(data => {
            document.getElementById("m_name").textContent = data.name;
            document.getElementById("m_email").textContent = data.email;
            document.getElementById("m_designation").textContent = data.designation;
            document.getElementById("m_role").textContent = data.role;
            document.getElementById("m_joined_system").textContent = data.joined_system;

            document.getElementById("m_total").textContent = data.total;
            document.getElementById("m_completed").textContent = data.completed;
            document.getElementById("m_pending").textContent = data.pending;
            document.getElementById("m_overdue").textContent = data.overdue;

            let percentage = data.total > 0 ? Math.round((data.completed / data.total) * 100) : 0;
            let progressBar = document.getElementById("m_progress");
            progressBar.style.width = percentage + "%";
            progressBar.textContent = percentage + "%";

            let modal = new bootstrap.Modal(document.getElementById("memberOverviewModal"));
            modal.show();
        })
        .catch(error => {
            alert("Error loading member details");
            console.error(error);
        });
}

// ========== PROFILE PAGE ==========
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
        if (badge) badge.style.display = 'inline-block';
    } else {
        form.classList.remove('edit-mode');
        btn.innerHTML = '<i class="fas fa-edit me-2"></i>Edit Profile';
        btn.classList.remove('btn-outline-secondary');
        btn.classList.add('btn-primary');
        if (badge) badge.style.display = 'none';
    }
}

function enableEdit(field) {
    if (!editMode) toggleEditMode();
    const input = document.querySelector(`[name="${field}"]`);
    if (input) input.focus();
}

function cancelEdit() {
    toggleEditMode();
    location.reload();
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
            location.reload();
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

// ========== DOM CONTENT LOADED ==========
document.addEventListener('DOMContentLoaded', function() {

    // ---- Message form submission (my_team) ----
    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', function (e) {
            e.preventDefault();
            let message = document.getElementById('messageText').value;
            if (!message.trim()) {
                alert('Please enter a message');
                return;
            }
            alert('Message sent successfully!');
            bootstrap.Modal.getInstance(document.getElementById('messageModal')).hide();
            this.reset();
        });
    }

    // ---- Email report form ----
    const emailForm = document.getElementById('emailReportForm');
    if (emailForm) {
        emailForm.onsubmit = function(e) {
            e.preventDefault();

            const formData = new FormData(emailForm);
            const submitBtn = emailForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Sending...';

            fetch("/projectleader/email_report", {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Report sent successfully!');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('emailModal'));
                    if (modal) modal.hide();
                    emailForm.reset();
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

            return false;
        };
    }

    // ---- Approve task buttons ----
    document.querySelectorAll('.approve-task').forEach(btn => {
        btn.addEventListener('click', function (e) {
            currentTaskId = this.dataset.taskId;
            new bootstrap.Modal(document.getElementById('approveTaskModal')).show();
        });
    });

    // ---- Reject task buttons ----
    document.querySelectorAll('.reject-task').forEach(btn => {
        btn.addEventListener('click', function (e) {
            currentTaskId = this.dataset.taskId;
            document.getElementById('rejectionReason').value = '';
            new bootstrap.Modal(document.getElementById('rejectTaskModal')).show();
        });
    });

    // ---- Edit task buttons (NEW) ----
    document.querySelectorAll('.edit-task').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const taskId = this.dataset.taskId;
            if (taskId) editTask(taskId);
        });
    });

    // ---- Delete task buttons (NEW) ----
    document.querySelectorAll('.delete-task').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const taskId = this.dataset.taskId;
            const taskName = this.dataset.taskName || 'this task';
            if (taskId) deleteTask(taskId, taskName);
        });
    });

    // ---- Confirm approve ----
    const confirmApproveBtn = document.getElementById('confirmApproveBtn');
    if (confirmApproveBtn) {
        confirmApproveBtn.addEventListener('click', function () {
            if (!currentTaskId) return;
            const btn = this;
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = 'Approving...';

            fetch(`/projectleader/approve_task/${currentTaskId}`, { method: 'POST' })
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert('✅ Task approved');
                        location.reload();
                    } else {
                        alert('❌ Error: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    alert('❌ Error: ' + error.message);
                })
                .finally(() => {
                    btn.disabled = false;
                    btn.innerHTML = originalText;
                    bootstrap.Modal.getInstance(document.getElementById('approveTaskModal')).hide();
                    currentTaskId = null;
                });
        });
    }

    // ---- Confirm reject ----
    const confirmRejectBtn = document.getElementById('confirmRejectBtn');
    if (confirmRejectBtn) {
        confirmRejectBtn.addEventListener('click', function () {
            if (!currentTaskId) return;
            const reason = document.getElementById('rejectionReason').value.trim();
            if (!reason) {
                alert('Please provide a rejection reason');
                return;
            }

            fetch(`/projectleader/reject_task/${currentTaskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason: reason })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ Task rejected');
                        location.reload();
                    } else {
                        alert('❌ Error: ' + data.error);
                    }
                })
                .catch(error => {
                    alert('❌ Error: ' + error);
                })
                .finally(() => {
                    bootstrap.Modal.getInstance(document.getElementById('rejectTaskModal')).hide();
                    currentTaskId = null;
                });
        });
    }

    // ---- Photo upload handling ----
    const photoUpload = document.getElementById('photoUpload');
    if (photoUpload) {
        photoUpload.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const formData = new FormData();
                formData.append('photo', file);

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
    }
});