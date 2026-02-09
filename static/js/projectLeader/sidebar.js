// Toggle Sidebar
function toggleSidebar() {
    const sb = document.getElementById('sidebar');
    const mc = document.getElementById('main-content');
    const icon = document.getElementById('toggle-icon');

    sb.classList.toggle('collapsed');
    mc.classList.toggle('expanded');
}

// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
    if (window.innerWidth <= 768) {
        document.addEventListener('click', function (e) {
            if (!e.target.closest('.sidebar') && !e.target.closest('.toggle-btn')) {
                document.getElementById('sidebar').classList.remove('show');
            }
        });
    }
});