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
// ============================
// NAV + SMOOTH SCROLL (fixed)
// ============================

// Grab elements FIRST (so we can use them everywhere)
const nav = document.querySelector("nav");
const toggle = document.querySelector(".nav-toggle");
const mobilePanel = document.querySelector(".nav-mobile");

// helper: open/close mobile menu + prevent background scroll
function setMenu(open) {
    if (!nav) return;

    nav.classList.toggle("menu-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");

    // lock body scroll when fullscreen menu is open
    document.body.style.overflow = open ? "hidden" : "";
}

// Toggle menu on hamburger
if (toggle && nav) {
    toggle.addEventListener("click", (e) => {
        e.stopPropagation(); // don't trigger outside-click close
        const open = !nav.classList.contains("menu-open");
        setMenu(open);
    });
}

// Close menu when clicking outside the menu panel (only when open)
document.addEventListener("click", (e) => {
    if (!nav || !nav.classList.contains("menu-open")) return;

    // if click is inside the mobile panel or on toggle button, ignore
    if (mobilePanel && mobilePanel.contains(e.target)) return;
    if (toggle && toggle.contains(e.target)) return;

    setMenu(false);
});

// Optional: close on ESC
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav?.classList.contains("menu-open")) {
        setMenu(false);
    }
});

// Smooth scroll for in-page anchors (works on mobile + desktop)
document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
        const href = a.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        // close fullscreen menu first (if open)
        const wasOpen = nav?.classList.contains("menu-open");
        if (wasOpen) setMenu(false);

        // allow layout to settle before scrolling (important on mobile)
        setTimeout(() => {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
            history.replaceState(null, "", href);
        }, wasOpen ? 80 : 0);
    });
});

// ============================
// Reveal-on-scroll (unchanged)
// ============================
const ro = new IntersectionObserver(
    (entries) => {
        entries.forEach((e) => {
            if (e.isIntersecting) e.target.classList.add("in");
        });
    },
    { threshold: 0.1 }
);
document.querySelectorAll(".r").forEach((el) => ro.observe(el));