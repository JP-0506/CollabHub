// Project specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Project search
    const searchInput = document.querySelector('.project-search');
    const filterSelect = document.querySelector('.project-filter');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterProjects();
        });
    }
    
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            filterProjects();
        });
    }
    
    // Add Project Modal functionality (NEW)
    const saveProjectBtn = document.getElementById('saveProjectBtn');
    
    if (saveProjectBtn) {
        saveProjectBtn.addEventListener('click', function() {
            const form = document.getElementById('addProjectForm');
            if (form.checkValidity()) {
                // Here you would typically send data to your backend
                const modal = bootstrap.Modal.getInstance(document.getElementById('addProjectModal'));
                modal.hide();
                
                alert('Project created successfully!');
                form.reset();
                document.getElementById('progressValue').textContent = '0%';
            } else {
                form.reportValidity();
            }
        });
    }
    
    // Progress slider update (NEW)
    const progressSlider = document.getElementById('projectProgress');
    const progressValue = document.getElementById('progressValue');
    
    if (progressSlider && progressValue) {
        progressSlider.addEventListener('input', function() {
            progressValue.textContent = this.value + '%';
        });
    }
    
    // Set default dates (NEW)
    const startDate = document.getElementById('startDate');
    const dueDate = document.getElementById('dueDate');
    
    if (startDate) {
        startDate.valueAsDate = new Date();
    }
    
    if (dueDate) {
        const nextMonth = new Date();
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        dueDate.valueAsDate = nextMonth;
    }
});

function filterProjects() {
    const searchTerm = document.querySelector('.project-search')?.value.toLowerCase() || '';
    const statusFilter = document.querySelector('.project-filter')?.value || '';
    
    const rows = document.querySelectorAll('.custom-table tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const status = row.querySelector('.status-badge')?.textContent || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesStatus = !statusFilter || status.includes(statusFilter);
        
        row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    });
}