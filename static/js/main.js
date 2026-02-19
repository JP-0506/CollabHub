// --- AUTO CLOSE MENU LOGIC ---
document.addEventListener("DOMContentLoaded", function () {
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    const navbarCollapse = document.getElementById('navbarNav');

    if (mobileLinks && navbarCollapse) {
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Check if menu is open (Bootstrap 'show' class)
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    // Use Bootstrap API to hide
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: true
                    });
                    bsCollapse.hide();
                }
            });
        });
    }
});
 // Approve task function
let currentTaskId = null;

function approveTask(taskId) {
    currentTaskId = taskId;
    let approveModal = new bootstrap.Modal(document.getElementById('approveTaskModal'));
    approveModal.show();
}