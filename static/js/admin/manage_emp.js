/****************** manage_emp.js ************************/


// =======================
// Employee Page Init
// =======================
document.addEventListener("DOMContentLoaded", function () {

    initEmployeeSearch();
    initPasswordValidation();
});


// =======================
// Search & Filter
// =======================
function initEmployeeSearch() {

    const searchInput = document.querySelector('.employee-search');
    const filterSelect = document.querySelector('.employee-filter');

    if (searchInput) {
        searchInput.addEventListener('input', filterEmployees);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterEmployees);
    }
}


// =======================
// Password Validation
// =======================
function initPasswordValidation() {

    const password = document.getElementById('password');
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


// =======================
// Filter Employees
// =======================
function filterEmployees() {

    const searchTerm =
        document.querySelector('.employee-search')?.value.toLowerCase() || '';

    const deptFilter =
        document.querySelector('.employee-filter')?.value || '';

    const rows = document.querySelectorAll('.custom-table tbody tr');

    rows.forEach(row => {

        const text = row.textContent.toLowerCase();

        const deptCell = row.children[2]?.textContent || '';

        const matchesSearch = text.includes(searchTerm);

        const matchesDept = !deptFilter || deptCell.includes(deptFilter);

        row.style.display =
            (matchesSearch && matchesDept) ? '' : 'none';
    });
}
