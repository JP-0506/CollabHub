/* =========================
   PROFILE EDIT / SAVE
========================= */

let editing = false;

function toggleEditProfile() {
    const nameSpan = document.getElementById("profile-name");
    const emailSpan = document.getElementById("profile-email");
    const roleSpan = document.getElementById("profile-role");

    const nameInput = document.getElementById("edit-name");
    const emailInput = document.getElementById("edit-email");
    const roleInput = document.getElementById("edit-role");

    const btn = document.getElementById("editBtn");

    if (!editing) {
        nameInput.value = nameSpan.innerText;
        emailInput.value = emailSpan.innerText;
        roleInput.value = roleSpan.innerText;

        nameSpan.classList.add("d-none");
        emailSpan.classList.add("d-none");
        roleSpan.classList.add("d-none");

        nameInput.classList.remove("d-none");
        emailInput.classList.remove("d-none");
        roleInput.classList.remove("d-none");

        btn.innerText = "Save Profile";
        btn.classList.replace("btn-primary", "btn-success");

        editing = true;
    } else {
        nameSpan.innerText = nameInput.value;
        emailSpan.innerText = emailInput.value;
        roleSpan.innerText = roleInput.value;

        nameSpan.classList.remove("d-none");
        emailSpan.classList.remove("d-none");
        roleSpan.classList.remove("d-none");

        nameInput.classList.add("d-none");
        emailInput.classList.add("d-none");
        roleInput.classList.add("d-none");

        btn.innerText = "Edit Profile";
        btn.classList.replace("btn-success", "btn-primary");

        editing = false;
    }
}

/* =========================
   SIDEBAR TOGGLE
========================= */

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("collapsed");
}

/* =========================
   IFRAME PAGE LOADER
========================= */

function loadPage(page, element) {
    document.getElementById("contentFrame").src = page;

    document.querySelectorAll(".nav-item").forEach(item =>
        item.classList.remove("active")
    );

    element.classList.add("active");
}

/* =========================
   LOGOUT
========================= */

function logout() {
    window.location.href = "../index.html";
}
