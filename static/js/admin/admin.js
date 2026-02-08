/****************** admin.js ************************/


// Toggle Sidebar
function toggleSidebar() {

    const sb = document.getElementById('sidebar');
    const mc = document.getElementById('main-content');

    sb.classList.toggle('collapsed');
    mc.classList.toggle('expanded');
}


// =======================
// Load Section From Flask
// =======================
async function loadSection(url) {

    try {

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Failed to load section");
        }

        const html = await response.text();

        const content = document.getElementById("content-area");

        content.innerHTML = html;

        content.classList.add("fade-in");

        setActiveNav(url);

        initializeSection();


    } catch (error) {

        console.error(error);

        document.getElementById("content-area").innerHTML = `
            <div class="alert alert-danger">
                Failed to load content.
            </div>
        `;
    }
}


// =======================
// Initialize Section JS
// =======================
function initializeSection() {

    // Cards / Modals
    initActionCards();

    // Form validation
    initForms();

    // Delete buttons
    initDeleteButtons();

    // Section specific
    if (typeof initEmployees === "function") initEmployees();
    if (typeof initProjects === "function") initProjects();
    if (typeof initProfile === "function") initProfile();
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

    contentArea.insertBefore(alertDiv, contentArea.firstChild);

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
// Navigation
// =======================
function initNavigation() {

    document
        .querySelectorAll(".nav-item[data-url]")
        .forEach(item => {

            item.addEventListener("click", function (e) {

                e.preventDefault();

                const url = this.dataset.url;

                loadSection(url);
            });
        });
}


// =======================
// Active Menu
// =======================
function setActiveNav(url) {

    document.querySelectorAll(".nav-item").forEach(item => {

        item.classList.remove("active");

        if (item.dataset.url === url) {

            item.classList.add("active");
        }
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


    // Mobile sidebar
    if (window.innerWidth <= 768) {

        document.addEventListener('click', function (e) {

            if (!e.target.closest('.sidebar') &&
                !e.target.closest('.toggle-btn')) {

                document
                    .getElementById('sidebar')
                    .classList.remove('show');
            }
        });
    }


    // Default page
    loadSection("/admin/dashboard");

});
