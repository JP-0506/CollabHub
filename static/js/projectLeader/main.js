// Switch Navigation - For Single Page Apps
function switchNav(id, el = null) {
    document.querySelectorAll('.section-view').forEach(v => v.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    if (el) {
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        el.classList.add('active');
    }
}

// Initialize tooltips for collapsed sidebar
document.addEventListener('DOMContentLoaded', function () {
    // Initialize dropdowns and other Bootstrap components
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function (e) {
            e.preventDefault();
            const dropdownMenu = this.nextElementSibling;
            dropdownMenu.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        if (!e.target.matches('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});