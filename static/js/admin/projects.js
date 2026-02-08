/****************** projects.js ************************/


// ============================
// Page Init
// ============================
document.addEventListener("DOMContentLoaded", function () {

    initProjects();

});


// ============================
// Initialize
// ============================
function initProjects() {

    initSearchFilter();

    initAddProjectModal();

    initProgressSlider();

    initDefaultDates();
}


// ============================
// Search & Filter
// ============================
function initSearchFilter() {

    const searchInput =
        document.querySelector('.project-search');

    const filterSelect =
        document.querySelector('.project-filter');


    if (searchInput) {
        searchInput.addEventListener('input', filterProjects);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterProjects);
    }
}


// ============================
// Filter Logic
// ============================
function filterProjects() {

    const searchTerm =
        document.querySelector('.project-search')
            ?.value.toLowerCase() || '';

    const statusFilter =
        document.querySelector('.project-filter')
            ?.value.toLowerCase() || '';


    const rows =
        document.querySelectorAll(
            '.custom-table tbody tr'
        );


    rows.forEach(row => {

        const text =
            row.textContent.toLowerCase();

        const status =
            row.querySelector('.status-badge')
                ?.textContent.toLowerCase() || '';


        const matchesSearch =
            text.includes(searchTerm);

        const matchesStatus =
            !statusFilter ||
            status.includes(statusFilter);


        row.style.display =
            (matchesSearch && matchesStatus)
                ? ''
                : 'none';
    });
}


// ============================
// Add Project Modal
// ============================
function initAddProjectModal() {

    const saveProjectBtn =
        document.getElementById('saveProjectBtn');


    if (!saveProjectBtn) return;


    saveProjectBtn.addEventListener('click', function () {

        const form =
            document.getElementById('addProjectForm');

        if (!form) return;


        if (!form.checkValidity()) {

            form.reportValidity();
            return;
        }


        // Let form submit to Flask
        form.submit();
    });
}


// ============================
// Progress Slider
// ============================
function initProgressSlider() {

    const progressSlider =
        document.getElementById('projectProgress');

    const progressValue =
        document.getElementById('progressValue');


    if (!progressSlider || !progressValue) return;


    progressSlider.addEventListener('input', function () {

        progressValue.textContent =
            this.value + '%';
    });
}


// ============================
// Default Dates
// ============================
function initDefaultDates() {

    const startDate =
        document.getElementById('startDate');

    const dueDate =
        document.getElementById('dueDate');


    if (startDate) {
        startDate.valueAsDate = new Date();
    }


    if (dueDate) {

        const nextMonth = new Date();

        nextMonth.setMonth(
            nextMonth.getMonth() + 1
        );

        dueDate.valueAsDate = nextMonth;
    }
}
