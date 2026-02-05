// Employee specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Employee search
    const searchInput = document.querySelector('.employee-search');
    const filterSelect = document.querySelector('.employee-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterEmployees();
        });
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            filterEmployees();
        });
    }
    
    // Add Employee Modal functionality (NEW)
    const saveEmployeeBtn = document.getElementById('saveEmployeeBtn');
    
    if (saveEmployeeBtn) {
        saveEmployeeBtn.addEventListener('click', function() {
            const form = document.getElementById('addEmployeeForm');
            if (form.checkValidity()) {
                // Here you would typically send data to your backend
                // For now, just close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addEmpModal'));
                modal.hide();
                
                // Show success message
                alert('Employee added successfully!');
                
                // Reset form
                form.reset();
            } else {
                // Trigger HTML5 validation
                form.reportValidity();
            }
        });
    }
    
    // Password confirmation validation (NEW)
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
});

function filterEmployees() {
    const searchTerm = document.querySelector('.employee-search')?.value.toLowerCase() || '';
    const deptFilter = document.querySelector('.employee-filter')?.value || '';
    
    const rows = document.querySelectorAll('.custom-table tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const deptCell = row.children[2]?.textContent || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesDept = !deptFilter || deptCell.includes(deptFilter);
        
        row.style.display = (matchesSearch && matchesDept) ? '' : 'none';
    });
}