from flask import Blueprint, render_template, session, redirect, url_for

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


# ============================
# ADMIN MAIN DASHBOARD
# ============================
@admin_bp.route("/")
def admin_home():

    # Login check
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Role check
    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("admin.html")


# ============================
# DASHBOARD SECTION
# ============================
@admin_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("section/dashboard.html")


# ============================
# PROJECTS SECTION
# ============================
@admin_bp.route("/projects")
def projects():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("section/projects.html")


# ============================
# EMPLOYEES SECTION
# ============================
@admin_bp.route("/employees")
def employees():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("section/manage_emp.html")


# ============================
# ASSIGN LEADER SECTION
# ============================
@admin_bp.route("/assign-leader")
def assign_leader():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("section/assign_leader.html")


# ============================
# PROFILE SECTION
# ============================
@admin_bp.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("section/profile.html")
