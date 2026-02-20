let isEditing = false;

function editProfile() {
  const nameSpan = document.getElementById("profile-name");
  const emailSpan = document.getElementById("profile-email");

  const nameInput = document.getElementById("edit-name");
  const emailInput = document.getElementById("edit-email");

  const btn = document.getElementById("editBtn");

  if (!nameSpan || !emailSpan || !nameInput || !emailInput || !btn) return;

  if (!isEditing) {
    // 👉 ENTER EDIT MODE
    nameInput.value = nameSpan.textContent.trim();
    emailInput.value = emailSpan.textContent.trim();

    nameSpan.classList.add("d-none");
    emailSpan.classList.add("d-none");

    nameInput.classList.remove("d-none");
    emailInput.classList.remove("d-none");

    btn.innerHTML = '<i class="fa fa-save me-1"></i> Save Changes';
    btn.classList.replace("btn-primary", "btn-success");

    isEditing = true;

  } else {
    // 👉 SAVE TO BACKEND
    const form = document.getElementById("profileForm");
    if (form) form.submit();   // backend will reload page
  }
}
/* ================= Change password security ================= */

function showMsg(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("d-none");
}

function hideMsg(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.add("d-none");
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("passwordForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideMsg("pass-error");
    hideMsg("pass-success");

    const btn = document.getElementById("passBtn");
    btn.disabled = true;
    btn.textContent = "Updating...";

    const payload = {
      current_password: document.getElementById("currentPassword").value.trim(),
      new_password: document.getElementById("newPassword").value.trim(),
      confirm_password: document.getElementById("confirmPassword").value.trim(),
    };

    try {
      const res = await fetch("/employee/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        showMsg("pass-error", data.message || "Server error");
      } else {
        showMsg("pass-success", data.message || "Password changed ✅");

        // clear inputs
        document.getElementById("currentPassword").value = "";
        document.getElementById("newPassword").value = "";
        document.getElementById("confirmPassword").value = "";

        // optional popup alert
        alert("Password changed successfully ✅");
      }
    } catch (err) {
      console.error(err);
      showMsg("pass-error", "Server error. Please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Update Password";
    }
  });
});

/* ================= SIDEBAR ================= */

function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  const mc = document.getElementById('main-content');
  const icon = document.getElementById('toggle-icon');

  sb.classList.toggle('collapsed');
  mc.classList.toggle('expanded');
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".submit-btn").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const form = this.closest("form");
      const taskId = this.dataset.taskId;

      if (confirm("Submit this task for leader review?")) {
        fetch(form.action, { method: "POST" })
          .then((res) => res.json())
          .then((data) => {
            if (data.success) {
              alert("Task submitted successfully!");
              location.reload();
            } else {
              alert("Error: " + data.message);
            }
          })
          .catch(() => alert("Error submitting task"));
      }
    });
  });
});