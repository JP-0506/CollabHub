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
    initDeleteButtons();

    if (document.getElementById("statusChart")) {
        loadProjectOverview();
    }

    if (document.getElementById("riskChart")) {
        loadRiskPanel();
    }

    if (document.getElementById("recentProjects")) {
        loadRecentProjects();
    }


    //for edit project detailsfrom edit modal
    initEditProjectModal();

    //for edit employee detailsfrom edit modal
    initEditEmployeeModal();



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

//     const modalEl = document.getElementById("addProjectModal");

//     if (!modalEl) return;

//     const modal = new bootstrap.Modal(modalEl);

//     const form = document.getElementById("projectForm");

//     const title = modalEl.querySelector(".modal-title");

//     const submitBtn = document.getElementById("projectSubmitBtn");


//     editBtns.forEach(btn => {

//         btn.addEventListener("click", function () {

//             // Get Data
//             const id = this.dataset.id;
//             const name = this.dataset.name;
//             const status = this.dataset.status;
//             const progress = this.dataset.progress;
//             const end = this.dataset.end;
//             const desc = this.dataset.desc;


//             // Fill Form
//             document.getElementById("projectId").value = id;
//             document.getElementById("projectName").value = name;
//             document.getElementById("projectStatus").value = status;
//             document.getElementById("projectProgress").value = progress || 0;
//             document.getElementById("projectEnd").value = end || "";
//             document.getElementById("projectDesc").value = desc || "";


//             // Change UI
//             title.textContent = "Edit Project";
//             submitBtn.textContent = "Update";


//             // Show Modal
//             modal.show();

//         });

//     });

// }

// // ============================
// // Reset Project Modal (Create)
// // ============================

// function initProjectCreateReset() {

//     const addBtn = document.querySelector(
//         '[data-bs-target="#addProjectModal"]'
//     );

//     const modalEl = document.getElementById("addProjectModal");

//     if (!addBtn || !modalEl) return;


//     addBtn.addEventListener("click", function () {

//         const form = document.getElementById("projectForm");

//         form.reset();

//         document.getElementById("projectId").value = "";


//         modalEl.querySelector(".modal-title")
//             .textContent = "Create New Project";

//         document.getElementById("projectSubmitBtn")
//             .textContent = "Create";

//     });

// }

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

                // 🔒 Disable dropdown
                leaderSelect.disabled = true;
            }

            /* =========================
               CASE 2 → No Leader
            ========================= */
            else {

                // Add "Select Leader" first
                const defaultOption = document.createElement("option");
                defaultOption.value = "";
                defaultOption.text = "Select Leader";
                defaultOption.selected = true;
                defaultOption.disabled = true;
                leaderSelect.appendChild(defaultOption);

                // Copy free leaders from create modal
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

                // If no free leaders exist
                if (leaderSelect.options.length === 1) {

                    const option = document.createElement("option");
                    option.value = "";
                    option.text = "No Free Leaders";
                    leaderSelect.appendChild(option);
                }
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

/****************** manage_emp.js ************************/
// ============================
// Edit Employee Modal
// ============================
function initEditEmployeeModal() {

    const editBtns = document.querySelectorAll(".edit-emp-btn");

    if (!editBtns.length) return;

    editBtns.forEach(btn => {

        btn.addEventListener("click", function () {

            const id = this.dataset.id;
            const name = this.dataset.name;
            const email = this.dataset.email;
            const designation = this.dataset.designation;
            const role = this.dataset.role;
            const status = this.dataset.status;

            // Helper to safely set value
            const setValue = (elementId, value) => {
                const el = document.getElementById(elementId);
                if (el) el.value = value || "";
            };

            setValue("editEmpId", id);
            setValue("editEmpName", name);
            setValue("editEmpEmail", email);
            setValue("editEmpDesignation", designation);
            setValue("editEmpRole", role);
            setValue("editEmpStatus", status);

            // Set form action dynamically
            const form = document.getElementById("editEmpForm");
            if (form) {
                form.action = "/admin/employee/edit/" + id;
            }

            // Open Bootstrap Modal
            const modalElement = document.getElementById("editEmpModal");

            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            }

        });

    });

}


