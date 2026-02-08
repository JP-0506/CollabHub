/****************** manage_emp ************************/

// Initialize Employee Section (Runs after fetch load)
function initEmployees() {

    // Employee search
    const searchInput = document.querySelector('.employee-search');
    const filterSelect = document.querySelector('.employee-filter');

    if (searchInput) {
        searchInput.addEventListener('input', filterEmployees);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterEmployees);
    }

    // Add Employee Modal functionality
    const saveEmployeeBtn = document.getElementById('saveEmployeeBtn');

    if (saveEmployeeBtn) {

        saveEmployeeBtn.addEventListener('click', function () {

            const form = document.getElementById('addEmployeeForm');

            if (!form) return;

            if (form.checkValidity()) {

                // (Later: Send to backend API here)

                const modalEl = document.getElementById('addEmpModal');
                const modal = bootstrap.Modal.getInstance(modalEl);

                if (modal) {
                    modal.hide();
                }

                // Show success
                alert('Employee added successfully!');

                // Reset form
                form.reset();

            } else {

                // Trigger HTML5 validation
                form.reportValidity();
            }
        });
    }

    // Password confirmation validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    if (password && confirmPassword) {

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
}


// Filter Employees
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