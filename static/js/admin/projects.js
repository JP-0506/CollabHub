/****************** projects ************************/

// Initialize Project Section (Runs after fetch load)
function initProjects() {

    // Project search
    const searchInput = document.querySelector('.project-search');
    const filterSelect = document.querySelector('.project-filter');

    if (searchInput) {
        searchInput.addEventListener('input', filterProjects);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterProjects);
    }

    // Add Project Modal functionality
    const saveProjectBtn = document.getElementById('saveProjectBtn');

    if (saveProjectBtn) {

        saveProjectBtn.addEventListener('click', function () {

            const form = document.getElementById('addProjectForm');

            if (!form) return;

            if (form.checkValidity()) {

                // (Later: Send data to backend API here)

                const modalEl = document.getElementById('addProjectModal');
                const modal = bootstrap.Modal.getInstance(modalEl);

                if (modal) {
                    modal.hide();
                }

                // Success message
                alert('Project created successfully!');

                // Reset form
                form.reset();

                const progressValue = document.getElementById('progressValue');

                if (progressValue) {
                    progressValue.textContent = '0%';
                }

            } else {

                // Trigger HTML5 validation
                form.reportValidity();
            }
        });
    }

    // Progress slider update
    const progressSlider = document.getElementById('projectProgress');
    const progressValue = document.getElementById('progressValue');

    if (progressSlider && progressValue) {

        progressSlider.addEventListener('input', function () {
            progressValue.textContent = this.value + '%';
        });
    }

    // Set default dates
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
}


// Filter Projects
function filterProjects() {

    const searchTerm =
        document.querySelector('.project-search')?.value.toLowerCase() || '';

    const statusFilter =
        document.querySelector('.project-filter')?.value || '';

    const rows = document.querySelectorAll('.custom-table tbody tr');

    rows.forEach(row => {

        const text = row.textContent.toLowerCase();

        const status =
            row.querySelector('.status-badge')?.textContent || '';

        const matchesSearch = text.includes(searchTerm);

        const matchesStatus =
            !statusFilter || status.includes(statusFilter);

        row.style.display =
            (matchesSearch && matchesStatus) ? '' : 'none';
    });
}
