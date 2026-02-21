/****************** admin.js ************************/


// =======================
// Toggle Sidebar
// =======================
function toggleSidebar() {

    const sb = document.getElementById('sidebar');
    const mc = document.getElementById('main-content');
    const icon = document.getElementById('toggle-icon');

    sb.classList.toggle('collapsed');
    mc.classList.toggle('expanded');
}


// =======================
// UI Helpers
// =======================

function initActionCards() {

    const actionCards = document.querySelectorAll('.action-card');

    actionCards.forEach(card => {

        card.addEventListener('click', function () {

            const target = this.dataset.target;

            if (target) {

                const modal = new bootstrap.Modal(
                    document.getElementById(target)
                );

                modal.show();
            }
        });
    });
}


function initForms() {

    const forms = document.querySelectorAll('form');

    forms.forEach(form => {

        form.addEventListener('submit', function (e) {

            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}


function initDeleteButtons() {

    const deleteBtns = document.querySelectorAll('.btn-outline-danger');

    deleteBtns.forEach(btn => {

        btn.addEventListener('click', function () {

            const row = this.closest('tr');

            if (confirm('Are you sure you want to delete this item?')) {

                row.style.opacity = '0.5';

                setTimeout(() => row.remove(), 300);
            }
        });
    });
}


// =======================
// Validation
// =======================
function validateForm(form) {

    let isValid = true;
    const errors = [];


    // Required fields
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {

        if (!field.value.trim()) {

            errors.push(`${field.name || field.placeholder} is required`);

            field.classList.add('is-invalid');

            isValid = false;

        } else {

            field.classList.remove('is-invalid');
        }
    });


    // Username rule
    const usernameInputs =
        form.querySelectorAll('input[name="username"], input[placeholder*="username"]');

    usernameInputs.forEach(input => {

        if (input.value && /^[_@0-9]/.test(input.value)) {

            errors.push("Username should not start with _, @ or number");

            input.classList.add('is-invalid');

            isValid = false;
        }
    });


    // Password length
    const passwordInputs = form.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(input => {

        if (input.value &&
            (input.value.length < 6 || input.value.length > 12)) {

            errors.push("Password must be 6 to 12 characters");

            input.classList.add('is-invalid');

            isValid = false;
        }
    });


    if (errors.length > 0) {
        showAlert(errors.join('<br>'), 'danger');
    }

    return isValid;
}


// =======================
// Alerts
// =======================
function showAlert(message, type = 'info') {

    const alertDiv = document.createElement('div');

    alertDiv.className =
        `alert alert-${type} alert-dismissible fade show`;

    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

    const contentArea = document.getElementById('content-area');

    if (contentArea) {
        contentArea.insertBefore(alertDiv, contentArea.firstChild);
    }

    setTimeout(() => alertDiv.remove(), 5000);
}


// =======================
// Global Search
// =======================
function initGlobalSearch() {

    const search = document.getElementById('globalSearch');

    if (!search) return;

    search.addEventListener('input', function (e) {

        const term = e.target.value.toLowerCase();

        const rows =
            document.querySelectorAll('.custom-table tbody tr');

        rows.forEach(row => {

            const text = row.textContent.toLowerCase();

            row.style.display =
                text.includes(term) ? '' : 'none';
        });
    });
}


// =======================
// Keyboard Shortcuts
// =======================
function initShortcuts() {

    document.addEventListener('keydown', function (event) {

        // Ctrl + /
        if (event.ctrlKey && event.key === '/') {

            event.preventDefault();

            document.getElementById('globalSearch')?.focus();
        }

        // ESC
        if (event.key === 'Escape') {

            const modals =
                document.querySelectorAll('.modal.show');

            modals.forEach(modal => {

                bootstrap.Modal.getInstance(modal)?.hide();
            });
        }
    });
}


// =======================
// Navigation (NORMAL ROUTING)
// =======================
function initNavigation() {

    document
        .querySelectorAll(".nav-item[data-url]")
        .forEach(item => {

            item.addEventListener("click", function () {

                const url = this.dataset.url;

                // 👉 NORMAL PAGE REDIRECT
                window.location.href = url;
            });
        });
}


// =======================
// Notifications
// =======================
function initNotifications() {

    const notificationBtn =
        document.querySelector('.notification-btn');

    if (!notificationBtn) return;

    notificationBtn.addEventListener('click', function () {

        document.querySelector('.notification-badge').textContent = '0';

        localStorage.setItem(
            'notificationsRead',
            new Date().toISOString()
        );
    });
}


// =======================
// Settings (LocalStorage)
// =======================
function saveSettings(key, value) {

    localStorage.setItem(`admin_${key}`, JSON.stringify(value));
}


function loadSettings(key, defaultValue) {

    const value = localStorage.getItem(`admin_${key}`);

    return value ? JSON.parse(value) : defaultValue;
}


function toggleTheme() {

    const current = loadSettings('theme', 'light');

    const next = current === 'light' ? 'dark' : 'light';

    saveSettings('theme', next);

    document.body.setAttribute('data-theme', next);
}


// =======================
// MAIN ENTRY POINT
// =======================
document.addEventListener("DOMContentLoaded", function () {

    initNavigation();

    initGlobalSearch();

    initShortcuts();

    initNotifications();

    initActionCards();
    initForms();
    // initDeleteButtons();


    if (document.getElementById("statusChart")) {
        loadProjectOverview();
    }

    if (document.getElementById("riskChart")) {
        loadRiskPanel();
    }

    if (document.getElementById("recentProjects")) {
        loadRecentProjects();
    }

    initProjectDateValidation();
    //for add member
    initAddEmployeeForm();
    //for edit project detailsfrom edit modal
    initEditProjectModal();
    /*to modal on click project avtar */
    initViewProject()


    //manage_emp.html
    //for edit employee detailsfrom edit modal
    initEditEmployeeModal();
    initDeleteEmployee();
    initViewEmployee();

    // 🔥 Projects page dynamic tables
    if (document.getElementById("allProjectsBody")) {
        loadAllProjects();
    }
    if (document.getElementById("pendingReviewBody")) {
        loadPendingReviewProjects();
    }
    if (document.getElementById("closedProjectsBody")) {
        loadClosedProjects();
    }



    // Mobile sidebar
    if (window.innerWidth <= 349) {

        document.addEventListener('click', function (e) {

            if (!e.target.closest('.sidebar') &&
                !e.target.closest('.toggle-btn')) {

                document
                    .getElementById('sidebar')
                    .classList.remove('show');
            }
        });
    }

});

// function goTo(url) {
//     window.location.href = url;
// }
function goTo(el) {

    const url = el.dataset.url;

    if (url) {
        window.location.href = url;
    }
}


// ============================
// Set Progress Bar Width
// ============================

document.addEventListener("DOMContentLoaded", function () {

    const bars = document.querySelectorAll(".progress-bar");

    bars.forEach(bar => {

        let width = bar.dataset.width;

        if (!width) width = 0;

        bar.style.width = width + "%";

    });

});

/*for dashboard admin ================= PROJECT OVERVIEW ================= */

// document.addEventListener("DOMContentLoaded", () => {

//     loadProjectOverview();
//     loadRiskPanel();
//     loadRecentProjects();

// });


// ================= PROJECT OVERVIEW =================

function loadProjectOverview() {

    fetch("/admin/api/project-status")
        .then(res => res.json())
        .then(data => {


            // ================= GET CANVAS =================

            const statusChart =
                document.getElementById("statusChart");

            const trendChart =
                document.getElementById("trendChart");

            const deadlineChart =
                document.getElementById("deadlineChart");

            const creationChart =
                document.getElementById("creationChart");


            // ================= STATUS DONUT =================

            new Chart(statusChart, {
                type: "doughnut",
                data: {
                    labels: data.status.map(s => s.status),
                    datasets: [{
                        data: data.status.map(s => s.total)
                    }]
                }
            });


            // ================= DEADLINE BAR =================

            new Chart(deadlineChart, {
                type: "bar",
                data: {
                    labels: data.deadline.map(d => d.project_name),
                    datasets: [{
                        label: "Progress %",
                        data: data.deadline.map(d => d.progress)
                    }]
                }
            });


            // ================= CREATION LINE =================

            new Chart(creationChart, {
                type: "line",
                data: {
                    labels: data.creation.map(c => c.month.substring(0, 7)),
                    datasets: [{
                        label: "Projects Created",
                        data: data.creation.map(c => c.total)
                    }]
                }
            });



            // ================= TREND (MULTI PROJECT) =================

            const trendData = data.trend;


            function randomColor() {

                return `hsl(${Math.random() * 360},70%,55%)`;
            }


            let datasets = [];


            Object.keys(trendData).forEach(project => {

                const values = trendData[project];

                // datasets.push({

                //     label: project,

                //     data: values.map(v => v.progress),

                //     borderColor: randomColor(),

                //     tension: 0.3,

                //     fill: false
                // });
                datasets.push({

                    label: project,

                    data: values.map(v => v.progress),

                    borderColor: randomColor(),

                    backgroundColor: "rgba(0,0,0,0.05)",

                    tension: 0.4,

                    fill: true,

                    pointStyle: "circle"
                });


            });


            // Safe labels
            let labels = [];

            if (Object.keys(trendData).length > 0) {

                labels =
                    trendData[Object.keys(trendData)[0]]
                        .map(v => v.month);
            }


            new Chart(trendChart, {

                type: "line",

                data: {
                    labels: labels,
                    datasets: datasets
                },

                options: {

                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    },

                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            ticks: {
                                callback: v => v + "%"
                            }
                        }
                    }
                }
            });


        });

}



// ================= RISK PANEL =================

function loadRiskPanel() {

    fetch("/admin/api/risk-projects")
        .then(res => res.json())
        .then(data => {


            const riskChart =
                document.getElementById("riskChart");


            new Chart(riskChart, {

                type: "bar",

                data: {
                    labels: data.map(r => r.project_name),
                    datasets: [{
                        label: "Progress %",
                        data: data.map(r => r.progress),
                        backgroundColor: "#ef4444"
                    }]
                }

            });

        });

}



// ================= RECENT PROJECTS =================

function loadRecentProjects() {

    fetch("/admin/api/recent-projects")
        .then(res => res.json())
        .then(data => {

            let html = "";

            data.forEach(p => {

                html += `
                    <tr>
                        <td>${p.project_name}</td>
                        <td>${p.status}</td>
                        <td>${p.progress}%</td>
                        <td>${p.end_date?.substring(0, 10)}</td>
                    </tr>
                `;

            });

            document.getElementById("recentProjects").innerHTML = html;

        });

}


// // ============================
// // Project Edit Modal Handler
// // ============================

// function initProjectEdit() {

//     const editBtns = document.querySelectorAll(".edit-btn");

//     editBtns.forEach(btn => {

//         btn.addEventListener("click", function () {

//             // Get data
//             const id = this.dataset.id;
//             const name = this.dataset.name;
//             const status = this.dataset.status;
//             const progress = this.dataset.progress;
//             const end = this.dataset.end;
//             const desc = this.dataset.desc;

//             // Fill modal
//             document.getElementById("projectId").value = id;
//             document.getElementById("projectName").value = name;
//             document.getElementById("projectStatus").value = status;
//             document.getElementById("projectProgress").value = progress || 0;
//             document.getElementById("projectEnd").value = end || "";
//             document.getElementById("projectDesc").value = desc || "";

//             // Change button text
//             document.getElementById("projectSubmitBtn").textContent = "Update";

//             // Change form action
//             document.getElementById("projectForm").action =
//                 "/admin/projects/edit/" + id;

//             // Open modal
//             new bootstrap.Modal(
//                 document.getElementById("addProjectModal")
//             ).show();

//         });

//     });
// }

// ============================
// Edit Project Modal
// ============================
function initEditProjectModal() {

    const editBtns = document.querySelectorAll(".edit-btn");
    if (!editBtns.length) return;

    editBtns.forEach(btn => {

        btn.addEventListener("click", function () {

            const id = this.dataset.id;
            const name = this.dataset.name;
            const status = this.dataset.status;
            const progress = this.dataset.progress;
            const start = this.dataset.start;
            const end = this.dataset.end;
            const desc = this.dataset.desc;
            const leaderId = this.dataset.leader;

            const row = this.closest("tr");
            const leaderCell = row ? row.children[1] : null;
            const leaderName = leaderCell ? leaderCell.innerText.trim() : "";

            const leaderSelect = document.getElementById("editProjectLeader");
            if (!leaderSelect) return;

            /* =========================
               RESET DROPDOWN
            ========================= */
            leaderSelect.innerHTML = "";
            leaderSelect.disabled = false;

            /* =========================
               CASE 1 → Leader Assigned
            ========================= */
            if (leaderId && leaderName && leaderName !== "-") {

                const option = document.createElement("option");
                option.value = leaderId;
                option.text = leaderName;
                option.selected = true;

                leaderSelect.appendChild(option);

                document.getElementById("hiddenLeaderId").value = leaderId;


                // 🔒 Disable dropdown
                leaderSelect.disabled = true;
            }

            /* =========================
               CASE 2 → No Leader
            ========================= */
            else {

                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "Select Leader";
                defaultOption.selected = true;
                defaultOption.disabled = true;
                leaderSelect.appendChild(defaultOption);

                const freeLeaders =
                    document.querySelectorAll("#projectLeader option");

                freeLeaders.forEach(opt => {
                    if (opt.value !== "") {
                        const option = document.createElement("option");
                        option.value = opt.value;
                        option.text = opt.text;
                        leaderSelect.appendChild(option);
                    }
                });

                // 👇 👇 👇 YAHI PASTE KARNA HAI
                leaderSelect.addEventListener("change", function () {
                    document.getElementById("hiddenLeaderId").value = this.value;
                });
            }

            /* =========================
               FILL OTHER FIELDS
            ========================= */
            const setValue = (fieldId, value) => {
                const el = document.getElementById(fieldId);
                if (el) el.value = value || "";
            };

            setValue("editProjectId", id);
            setValue("editProjectName", name);
            setValue("editProjectStatus", status);
            setValue("editProjectProgress", progress || 0);
            setValue("editProjectStart", start);
            setValue("editProjectEnd", end);
            setValue("editProjectDesc", desc);

            /* =========================
               SET FORM ACTION
            ========================= */
            const form = document.getElementById("editProjectForm");
            if (form) {
                form.action = "/admin/projects/edit/" + id;
            }

            /* =========================
               OPEN MODAL
            ========================= */
            const modalElement =
                document.getElementById("editProjectModal");

            if (modalElement) {
                const modal =
                    new bootstrap.Modal(modalElement);
                modal.show();
            }

        });

    });
}

/*to show modal when click project avtar*/
// ============================
// View Project Details (Two Column Layout)
// ============================
function initViewProject() {

    const viewBtns = document.querySelectorAll(".view-project-btn");

    viewBtns.forEach(btn => {
        btn.addEventListener("click", function () {

            const projectId = this.dataset.id;
            const projectName = this.dataset.name;
            const modal = new bootstrap.Modal(document.getElementById('viewProjectModal'));

            // Set title
            document.getElementById('viewProjectModalTitle').textContent = projectName;

            // Show loading
            document.getElementById('viewProjectDetails').innerHTML = `
                <div class="text-center py-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;

            modal.show();

            // Fetch project details
            fetch(`/admin/api/project/${projectId}`)
                .then(res => res.json())
                .then(data => {

                    if (data.error) {
                        throw new Error(data.error);
                    }

                    const project = data.project;
                    const members = data.members || [];

                    // Team Members HTML (Right Side)
                    let membersHtml = '';
                    if (members.length > 0) {
                        members.forEach(m => {
                            membersHtml += `
                                <div class="d-flex align-items-center mb-3">
                                    <div class="user-avatar me-2" style="width: 36px; height: 36px; font-size: 0.9rem; background: ${m.is_leader ? '#10b981' : '#6b7280'}; flex-shrink: 0;">
                                        ${m.name ? m.name.charAt(0).toUpperCase() : '?'}
                                    </div>
                                    <div>
                                        <div class="d-flex align-items-center">
                                            <strong>${m.name || 'Unknown'}</strong>
                                            ${m.is_leader ? '<span class="badge bg-success ms-2">Leader</span>' : ''}
                                        </div>
                                        <small class="text-muted d-block">${m.designation || 'Team Member'}</small>
                                    </div>
                                </div>
                            `;
                        });
                    } else {
                        membersHtml = '<p class="text-muted text-center py-3">No team members assigned</p>';
                    }

                    // Two Column Layout
                    document.getElementById('viewProjectDetails').innerHTML = `
                        <div class="row">
                            <!-- LEFT COLUMN - Project Details -->
                            <div class="col-md-6 border-end">
                                <div class="pe-3">
                                    <!-- Progress -->
                                    <div class="mb-4">
                                        <label class="fw-bold text-muted small">PROGRESS</label>
                                        <div class="d-flex align-items-center mt-1">
                                            <div class="progress-container flex-grow-1 me-2" style="height: 8px;">
                                                <div class="progress-bar" style="width:${project.progress || 0}%"></div>
                                            </div>
                                            <span class="badge bg-primary">${project.progress || 0}%</span>
                                        </div>
                                    </div>
                                    
                                    <!-- Leader -->
                                    <div class="mb-3">
                                        <label class="fw-bold text-muted small">TEAM LEADER</label>
                                        <p class="mb-0 fw-semibold">${project.leader_name || 'Not assigned'}</p>
                                    </div>
                                    
                                    <!-- Dates -->
                                    <div class="row mb-3">
                                        <div class="col-6">
                                            <label class="fw-bold text-muted small">START DATE</label>
                                            <p class="mb-0">${project.start_date || 'Not set'}</p>
                                        </div>
                                        <div class="col-6">
                                            <label class="fw-bold text-muted small">END DATE</label>
                                            <p class="mb-0">${project.end_date || 'Not set'}</p>
                                        </div>
                                    </div>
                                    
                                    <!-- Status -->
                                    <div class="mb-3">
                                        <label class="fw-bold text-muted small">STATUS</label>
                                        <p class="mb-0"><span class="status-badge status-${project.status || 'planning'}">${(project.status || 'planning').toUpperCase()}</span></p>
                                    </div>
                                    
                                    <!-- Description -->
                                    <div class="mb-3">
                                        <label class="fw-bold text-muted small">DESCRIPTION</label>
                                        <p class="mb-0">${project.description || 'No description provided'}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- RIGHT COLUMN - Team Members -->
                            <div class="col-md-6">
                                <div class="ps-3">
                                    <label class="fw-bold text-muted small mb-2">TEAM MEMBERS (${members.length})</label>
                                    <div style="max-height: 350px; overflow-y: auto;">
                                        ${membersHtml}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(err => {
                    document.getElementById('viewProjectDetails').innerHTML = `
                        <div class="alert alert-danger mb-0">
                            Error loading project details: ${err.message || 'Something went wrong'} ❌
                        </div>
                    `;
                });
        });
    });
}

// ============================
// Date Validation for Project Forms
// ============================
function initProjectDateValidation() {

    // For Create Project Modal
    const createForm = document.getElementById('projectForm');
    if (createForm) {
        const startDateInput = document.getElementById('projectStart');
        const endDateInput = document.getElementById('projectEnd');

        // Set min date to today for both inputs
        const today = new Date().toISOString().split('T')[0];
        if (startDateInput) {
            startDateInput.min = today;
        }
        if (endDateInput) {
            endDateInput.min = today;
        }

        // Override form submission
        createForm.onsubmit = function (e) {
            e.preventDefault();

            // Basic frontend validation first
            if (!validateProjectDates(startDateInput, endDateInput)) {
                return false;
            }

            // Submit via AJAX
            submitProjectForm(createForm, 'create');
            return false;
        };
    }

    // For Edit Project Modal
    const editForm = document.getElementById('editProjectForm');
    if (editForm) {
        const startDateInput = document.getElementById('editProjectStart');
        const endDateInput = document.getElementById('editProjectEnd');

        // Set min date to today for both inputs
        const today = new Date().toISOString().split('T')[0];
        if (startDateInput) {
            startDateInput.min = today;
        }
        if (endDateInput) {
            endDateInput.min = today;
        }

        // Override form submission
        editForm.onsubmit = function (e) {
            e.preventDefault();

            if (!validateProjectDates(startDateInput, endDateInput)) {
                return false;
            }

            const projectId = document.getElementById('editProjectId').value;
            submitProjectForm(editForm, 'edit', projectId);
            return false;
        };
    }
}

// Helper function to validate dates
function validateProjectDates(startInput, endInput) {

    // If both dates are empty, it's valid (dates are optional)
    if ((!startInput || !startInput.value) && (!endInput || !endInput.value)) {
        return true;
    }

    const today = new Date().toISOString().split('T')[0];

    // Check if start date is in the past
    if (startInput && startInput.value && startInput.value < today) {
        alert('Start date cannot be in the past');
        startInput.focus();
        return false;
    }

    // Check if end date is in the past
    if (endInput && endInput.value && endInput.value < today) {
        alert('End date cannot be in the past');
        endInput.focus();
        return false;
    }

    // Check if end date is before start date
    if (startInput && startInput.value && endInput && endInput.value) {
        if (endInput.value < startInput.value) {
            alert('End date must be after or equal to start date');
            endInput.focus();
            return false;
        }
    }

    return true;
}

// Submit project form via AJAX
function submitProjectForm(form, action, projectId = null) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Saving...';

    let url = '/admin/projects';
    if (action === 'edit' && projectId) {
        url = `/admin/projects/edit/${projectId}`;
    }

    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Close modal
                const modalId = action === 'edit' ? 'editProjectModal' : 'addProjectModal';
                const modalElement = document.getElementById(modalId);
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();

                // Show success message
                alert(data.message);

                // Reload page to show changes
                location.reload();
            } else {
                // Show error message directly from server
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        })
        .finally(() => {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
}

/****************** manage_emp.js ************************/

// ============================
// Add Employee Form Handler
// ============================
function initAddEmployeeForm() {
    const addForm = document.querySelector('#addEmpModal form');

    if (addForm) {
        addForm.onsubmit = async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';

            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.status === 'success') {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addEmpModal'));
                    if (modal) {
                        modal.hide();
                    }

                    // Show success message
                    alert(result.message);

                    // Reset form
                    this.reset();

                    // Reload page to show new employee
                    location.reload();

                } else {
                    // Show error message
                    alert(result.message || 'Error adding employee');
                }

            } catch (error) {
                console.error('Error adding employee:', error);
                alert('Network error. Please check your connection and try again.');

            } finally {
                // Reset button state
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        };
    }
}

// ============================
// Edit Employee Modal
// ============================
function initEditEmployeeModal() {

    const editBtns = document.querySelectorAll(".edit-emp-btn");

    if (!editBtns.length) return;

    editBtns.forEach(btn => {

        btn.addEventListener("click", function () {

            const id = this.dataset.id;
            const designation = this.dataset.designation;
            const role = this.dataset.role;

            document.getElementById("editEmpId").value = id;
            document.getElementById("editEmpDesignation").value = designation || "";
            document.getElementById("editEmpRole").value = role || "employee";

            const modalElement = document.getElementById("editEmpModal");
            const form = document.getElementById("editEmpForm");

            if (form) {
                // Remove any existing submit event listeners
                form.onsubmit = null;

                // Set form action
                form.action = "/admin/employee/edit/" + id;

                // Add new submit handler
                form.onsubmit = async function (e) {
                    e.preventDefault();

                    const formData = new FormData(form);

                    try {
                        const response = await fetch(form.action, {
                            method: 'POST',
                            body: formData
                        });

                        const result = await response.json();

                        if (result.status === 'success') {
                            // Show success alert
                            alert(result.message);
                            // Close modal
                            const modal = bootstrap.Modal.getInstance(modalElement);
                            if (modal) {
                                modal.hide();
                            }
                            // Reload page to show updated data
                            location.reload();
                        } else {
                            // Show error alert
                            alert(result.message);
                        }
                    } catch (error) {
                        alert('An error occurred while updating employee ❌');
                        console.error('Error:', error);
                    }
                };
            }

            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            }
        });
    });
}

// ============================
// Soft Delete Employee with Confirmation
// ============================
function initDeleteEmployee() {

    const deleteBtns = document.querySelectorAll(".delete-emp-btn");

    if (!deleteBtns.length) return;

    deleteBtns.forEach(btn => {

        btn.addEventListener("click", function () {

            const id = this.dataset.id;
            const name = this.dataset.name;

            // Show confirmation dialog
            if (confirm(`Are you sure you want to deactivate ${name}? They will no longer be able to access the system.`)) {

                // Create form data
                const formData = new FormData();
                formData.append('user_id', id);

                // Send delete request
                fetch(`/admin/employee/delete/${id}`, {
                    method: 'POST',
                    body: formData
                })
                    .then(response => response.json())
                    .then(result => {
                        if (result.status === 'success') {
                            alert(result.message);
                            location.reload(); // Reload to reflect changes
                        } else {
                            alert(result.message); // Show error message
                        }
                    })
                    .catch(error => {
                        alert('An error occurred while deactivating employee ❌');
                        console.error('Error:', error);
                    });
            }
        });
    });
}

// ============================
// View Employee Details
// ============================
function initViewEmployee() {

    const viewBtns = document.querySelectorAll(".view-emp-btn");

    viewBtns.forEach(btn => {
        btn.addEventListener("click", function () {

            const empId = this.dataset.id;
            const modal = new bootstrap.Modal(document.getElementById('viewEmpModal'));

            // Show loading
            document.getElementById('viewEmpDetails').innerHTML = `
                <div class="text-center py-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;

            modal.show();

            // Fetch employee details
            fetch(`/admin/api/employee/${empId}`)
                .then(res => res.json())
                .then(data => {

                    // Check if error occurred
                    if (data.error) {
                        throw new Error(data.error);
                    }

                    // Projects HTML
                    let projectsHtml = '';
                    if (data.projects && data.projects.length > 0) {
                        data.projects.forEach(p => {
                            projectsHtml += `<span class="badge bg-info me-1 mb-1">${p.project_name} (${p.status})</span>`;
                        });
                    } else {
                        projectsHtml = '<span class="text-muted">Not assigned to any project</span>';
                    }

                    // Team Members HTML with CSS classes
                    // Team Members HTML (compact version)
                    let teamHtml = '';
                    if (data.team_members && data.team_members.length > 0) {
                        teamHtml = '<div style="max-height: 400px; overflow-y: auto;">';
                        data.team_members.forEach(m => {
                            teamHtml += `
                                <div class="d-flex align-items-center mb-3">
                                    <div class="user-avatar me-2" style="width: 32px; height: 32px; font-size: 0.8rem; flex-shrink: 0;">
                                        ${m.name ? m.name[0].toUpperCase() : '?'}
                                    </div>
                                    <div>
                                        <strong style="font-size: 0.9rem;">${m.name || 'Unknown'}</strong>
                                        <small class="text-muted d-block" style="font-size: 0.8rem;">${m.role || 'employee'} (${m.project_role || 'Member'})</small>
                                    </div>
                                </div>
                            `;
                        });
                        teamHtml += '</div>';
                    } else {
                        teamHtml = '<p class="text-muted">No team members found</p>';
                    }
                    // Last Login HTML
                    let lastLoginHtml = 'Never';
                    if (data.last_login) {
                        try {
                            const date = new Date(data.last_login);
                            lastLoginHtml = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
                        } catch (e) {
                            lastLoginHtml = 'Invalid date';
                        }
                    }

                    document.getElementById('viewEmpDetails').innerHTML = `
                        <div class="row">
                            <!-- Left Column - Employee Details -->
                            <div class="col-md-6 border-end">
                                <div class="pe-3">
                                    <label class="fw-bold text-muted small">Full Name</label>
                                    <p class="mb-2">${data.employee?.name || '-'}</p>
                                    
                                    <label class="fw-bold text-muted small">Username</label>
                                    <p class="mb-2">${data.employee?.username || '-'}</p>
                                    
                                    <label class="fw-bold text-muted small">Email</label>
                                    <p class="mb-2">${data.employee?.email || '-'}</p>
                                    
                                    <label class="fw-bold text-muted small">Designation</label>
                                    <p class="mb-2">${data.employee?.designation || '-'}</p>
                                    
                                    <label class="fw-bold text-muted small">Role</label>
                                    <p class="mb-2">${data.employee?.role || '-'}</p>
                                    
                                    <label class="fw-bold text-muted small">Working On</label>
                                    <p class="mb-2">${projectsHtml}</p>
                                    
                                    <label class="fw-bold text-muted small mt-2">Last Active</label>
                                    <p class="mb-0">${lastLoginHtml}</p>
                                </div>
                            </div>
                            
                            <!-- Right Column - Team Members -->
                            <div class="col-md-6">
                                <div class="ps-3">
                                    <label class="fw-bold text-muted small">Team Members</label>
                                    ${teamHtml}
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(err => {
                    console.error('View employee error:', err);
                    document.getElementById('viewEmpDetails').innerHTML = `
                        <div class="alert alert-danger mb-0">
                            Error loading employee details: ${err.message || 'Something went wrong'} ❌
                        </div>
                    `;
                });
        });
    });
}

// ============================
// Pending Review - Load Projects
// ============================
function loadPendingReviewProjects() {

    const tbody = document.getElementById("pendingReviewBody");
    const countBadge = document.getElementById("pendingReviewCount");

    if (!tbody) return;

    fetch("/admin/api/pending_review_projects")
        .then(function (response) {
            return response.json();
        })
        .then(function (projects) {

            if (projects.length === 0) {
                tbody.innerHTML =
                    '<tr><td colspan="6" class="text-center text-muted py-3">No projects pending review</td></tr>';
                if (countBadge) countBadge.textContent = "0";
                return;
            }

            if (countBadge) countBadge.textContent = projects.length;

            let rows = "";

            projects.forEach(function (p) {
                rows += `
                    <tr id="review-row-${p.project_id}">
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="user-avatar me-3" style="background:#f59e0b; color:white;">
                                    ${p.project_name[0].toUpperCase()}
                                </div>
                                <div class="fw-bold">${p.project_name}</div>
                            </div>
                        </td>
                        <td>${p.leader_name || "-"}</td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="progress-container me-2" style="flex:1;">
                                    <div class="progress-bar" style="width:${p.progress || 0}%;"></div>
                                </div>
                                <small>${p.progress || 0}%</small>
                            </div>
                        </td>
                        <td>${p.start_date || "-"}</td>
                        <td>${p.end_date || "-"}</td>
                        <td>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-success"
                                    onclick="reviewProject(${p.project_id}, 'accept')">
                                    <i class="fas fa-check me-1"></i>Accept
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                    onclick="reviewProject(${p.project_id}, 'reject')">
                                    <i class="fas fa-times me-1"></i>Reject
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = rows;
        })
        .catch(function () {
            tbody.innerHTML =
                '<tr><td colspan="6" class="text-center text-danger py-3">Failed to load projects</td></tr>';
        });
}


// ============================
// Pending Review - Accept or Reject
// ============================
function reviewProject(projectId, action) {

    if (action === "accept") {

        if (!confirm("Are you sure you want to ACCEPT this project? Status will be set to Closed.")) return;

        sendReviewRequest(projectId, "accept", "");

    } else {

        // Show reject modal
        document.getElementById("rejectProjectId").value = projectId;
        document.getElementById("rejectReason").value = "";
        document.getElementById("rejectReasonError").style.display = "none";

        const rejectModal = new bootstrap.Modal(document.getElementById("rejectProjectModal"));
        rejectModal.show();
    }
}


function sendReviewRequest(projectId, action, reason) {

    fetch(`/admin/review_project/${projectId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: action, reason: reason })
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {

            if (data.status === "success") {

                // Close reject modal if open
                const rejectModalEl = document.getElementById("rejectProjectModal");
                if (rejectModalEl) {
                    const modalInstance = bootstrap.Modal.getInstance(rejectModalEl);
                    if (modalInstance) modalInstance.hide();
                }

                // Remove the row from pending table immediately
                const row = document.getElementById(`review-row-${projectId}`);
                if (row) row.remove();

                // Update pending badge count
                const countBadge = document.getElementById("pendingReviewCount");
                if (countBadge) {
                    const current = parseInt(countBadge.textContent) || 0;
                    countBadge.textContent = Math.max(0, current - 1);
                }

                // Show empty message if no rows left
                const tbody = document.getElementById("pendingReviewBody");
                if (tbody && tbody.querySelectorAll("tr").length === 0) {
                    tbody.innerHTML =
                        '<tr><td colspan="6" class="text-center text-muted py-3">No projects pending review</td></tr>';
                }

                // 🔥 Refresh both tables immediately (no alert blocking)
                loadClosedProjects();
                loadAllProjects();

                // Show non-blocking toast
                showToast(data.message, "success");

            } else {
                showToast("Error: " + data.message, "danger");
            }
        })
        .catch(function () {
            showToast("Something went wrong. Please try again.", "danger");
        });
}


// ============================
// Non-blocking Toast Notification
// ============================
function showToast(message, type = "success") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.style.cssText = "position:fixed;top:20px;right:20px;z-index:9999;";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `alert alert-${type} alert-dismissible shadow`;
    toast.style.cssText = "min-width:280px;animation:fadeIn 0.3s ease;";
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}


// ============================
// Load Closed Projects
// ============================
function loadClosedProjects() {

    const tbody = document.getElementById("closedProjectsBody");
    const countBadge = document.getElementById("closedProjectsCount");

    if (!tbody) return;

    fetch("/admin/api/closed_projects")
        .then(function (response) {
            return response.json();
        })
        .then(function (projects) {

            if (projects.length === 0) {
                tbody.innerHTML =
                    '<tr><td colspan="6" class="text-center text-muted py-3">No closed projects yet</td></tr>';
                if (countBadge) countBadge.textContent = "0";
                return;
            }

            if (countBadge) countBadge.textContent = projects.length;

            let rows = "";

            const fmt = d => d ? new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : "-";

            projects.forEach(function (p) {
                rows += `
                    <tr>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="user-avatar me-3" style="background:#6366f1; color:white;">
                                    ${p.project_name[0].toUpperCase()}
                                </div>
                                <div class="fw-bold">${p.project_name}</div>
                            </div>
                        </td>
                        <td>${p.leader_name || "-"}</td>
                        <td>${fmt(p.start_date)}</td>
                        <td>${fmt(p.end_date)}</td>
                        <td>${fmt(p.closed_at)}</td>
                        <td><span class="status-badge status-closed">Closed</span></td>
                    </tr>
                `;
            });

            tbody.innerHTML = rows;
        })
        .catch(function () {
            tbody.innerHTML =
                '<tr><td colspan="6" class="text-center text-danger py-3">Failed to load closed projects</td></tr>';
        });
}


// ============================
// Load All Projects (for dynamic refresh)
// ============================
function loadAllProjects() {
    const tbody = document.getElementById("allProjectsBody");
    if (!tbody) return;

    fetch("/admin/api/all_projects")
        .then(response => response.json())
        .then(function (projects) {
            if (projects.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No projects found</td></tr>';
                return;
            }

            let rows = "";
            projects.forEach(function (p) {
                const initial = p.project_name ? p.project_name[0].toUpperCase() : "P";
                const progress = p.progress || 0;
                const statusClass = `status-${p.status}`;
                const statusLabel = p.status ? p.status.charAt(0).toUpperCase() + p.status.slice(1) : "-";
                const endDate = p.end_date || "-";
                const leaderName = p.leader_name || "-";
                const memberCount = p.member_count || 0;

                rows += `
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="user-avatar me-3 view-project-btn" data-id="${p.project_id}"
                                data-name="${p.project_name}" style="cursor:pointer; background:#3b82f6;"
                                title="Click to view project details">
                                ${initial}
                            </div>
                            <div>
                                <div class="fw-bold">${p.project_name}</div>
                                <small class="text-muted">Project Team</small>
                            </div>
                        </div>
                    </td>
                    <td>${leaderName}</td>
                    <td>${memberCount}</td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="progress-container me-2" style="flex:1;">
                                <div class="progress-bar" style="width:${progress}%;"></div>
                            </div>
                            <small>${progress}%</small>
                        </div>
                    </td>
                    <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
                    <td>${endDate}</td>
                    <td>
                        <div class="d-flex gap-2">
                            <button type="button" class="btn btn-sm btn-outline-primary edit-btn"
                                data-id="${p.project_id}" data-name="${p.project_name}"
                                data-status="${p.status}" data-progress="${progress}"
                                data-start="${p.start_date || ''}" data-end="${p.end_date || ''}"
                                data-desc="${p.features || ''}" data-leader="${p.leader_id || ''}">
                                <i class="fas fa-edit"></i>
                            </button>
                        </div>
                    </td>
                </tr>`;
            });

            tbody.innerHTML = rows;
        })
        .catch(function () {
            console.error("Failed to reload All Projects table");
        });
}


// ============================
// Init on Projects Page
// ============================

// Confirm reject button inside modal
const confirmRejectBtn = document.getElementById("confirmRejectProjectBtn");
if (confirmRejectBtn) {
    confirmRejectBtn.addEventListener("click", function () {

        const projectId = document.getElementById("rejectProjectId").value;
        const reason = document.getElementById("rejectReason").value.trim();

        if (!reason) {
            document.getElementById("rejectReasonError").style.display = "block";
            return;
        }

        document.getElementById("rejectReasonError").style.display = "none";
        sendReviewRequest(projectId, "reject", reason);
    });
}