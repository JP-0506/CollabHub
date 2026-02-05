// Toggle Sidebar
function toggleSidebar() {
    const sb = document.getElementById('sidebar');
    const mc = document.getElementById('main-content');
    const icon = document.getElementById('toggle-icon');
    
    sb.classList.toggle('collapsed');
    mc.classList.toggle('expanded');
}

// Load Section Content
async function loadSection(sectionFile) {
    try {
        const response = await fetch(sectionFile);
        const html = await response.text();
        
        document.getElementById('content-area').innerHTML = html;
        document.getElementById('content-area').classList.add('fade-in');
        
        // Update active nav item - FIXED!
        const fileName = sectionFile.split('/').pop(); // Gets "dashboard.html" from "section/dashboard.html"
        
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.section === fileName) {  // Compare with just the filename
                item.classList.add('active');
            }
        });
        
        // Initialize any components in loaded section
        initializeSection();
    } catch (error) {
        console.error('Error loading section:', error);
        document.getElementById('content-area').innerHTML = `
            <div class="alert alert-danger">
                Error loading content. Please try again.
            </div>
        `;
    }
}

// Initialize Section Components
function initializeSection() {
    // Initialize any tooltips, modals, etc.
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const target = this.dataset.target;
            if (target) {
                const modal = new bootstrap.Modal(document.getElementById(target));
                modal.show();
            }
        });
    });
    
    // Form validation for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
    
    // Table row actions
    const deleteBtns = document.querySelectorAll('.btn-outline-danger');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            if (confirm('Are you sure you want to delete this item?')) {
                row.style.opacity = '0.5';
                setTimeout(() => row.remove(), 300);
            }
        });
    });
}

// Form Validation (From Syllabus Unit-10)
function validateForm(form) {
    let isValid = true;
    const errors = [];
    
    // Required fields validation
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
    
    // Username validation (no starting with _, @ or number)
    const usernameInputs = form.querySelectorAll('input[name="username"], input[placeholder*="username"]');
    usernameInputs.forEach(input => {
        if (input.value && /^[_@0-9]/.test(input.value)) {
            errors.push("Username should not start with _, @ or number");
            input.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Password length validation (6-12 characters)
    const passwordInputs = form.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.value && (input.value.length < 6 || input.value.length > 12)) {
            errors.push("Password must be 6 to 12 characters");
            input.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Show errors if any
    if (errors.length > 0) {
        showAlert(errors.join('<br>'), 'danger');
    }
    
    return isValid;
}

// Show Alert Message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const contentArea = document.getElementById('content-area');
    contentArea.insertBefore(alertDiv, contentArea.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

// Global Search
document.getElementById('globalSearch')?.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    // Search in tables
    const tables = document.querySelectorAll('.custom-table tbody tr');
    tables.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
});

// Keyboard Shortcuts (From Syllabus Unit-9)
document.addEventListener('keydown', function(event) {
    // Ctrl + / to focus search
    if (event.ctrlKey && event.key === '/') {
        event.preventDefault();
        document.getElementById('globalSearch')?.focus();
    }
    
    // Escape to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Set up navigation click handlers
    document.querySelectorAll('.nav-item[data-section]').forEach(item => {
        item.addEventListener('click', function(e) {
            if (!this.href) {
                e.preventDefault();
                const sectionFile = this.dataset.section;
                loadSection(`section/${sectionFile}`);  // Add "section/" prefix
            }
        });
    });
    
    // Mobile sidebar toggle
    if (window.innerWidth <= 768) {
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.toggle-btn')) {
                document.getElementById('sidebar').classList.remove('show');
            }
        });
    }
    
    // Initialize notifications
    const notificationBtn = document.querySelector('.notification-btn');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', function() {
            // Mark notifications as read
            document.querySelector('.notification-badge').textContent = '0';
            localStorage.setItem('notificationsRead', new Date().toISOString());
        });
    }
});

// Local Storage for Settings (From Syllabus Unit-10)
function saveSettings(key, value) {
    localStorage.setItem(`admin_${key}`, JSON.stringify(value));
}

function loadSettings(key, defaultValue) {
    const value = localStorage.getItem(`admin_${key}`);
    return value ? JSON.parse(value) : defaultValue;
}

// Example: Save theme preference
function toggleTheme() {
    const currentTheme = loadSettings('theme', 'light');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    saveSettings('theme', newTheme);
    document.body.setAttribute('data-theme', newTheme);
}
