from flask import Flask, render_template, redirect, session, url_for

from auth import auth_bp


app = Flask(__name__)

app.secret_key = "collabhub_secret_key"


# -----------------------------
# Register Blueprint
# -----------------------------
app.register_blueprint(auth_bp, url_prefix="/auth")


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin/section/dashboard")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    return render_template("admin/admin.html")


# -----------------------------
# LEADER DASHBOARD
# -----------------------------
@app.route("/projectleader/dashboard")
def leader_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "project_leader":
        return "Access Denied ❌"

    return render_template("projectLeader/dashboard.html")


# -----------------------------
# EMPLOYEE DASHBOARD
# -----------------------------
@app.route("/employee/dashboard")
def employee_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "employee":
        return "Access Denied ❌"

    return render_template("Employee/dashboard.html")


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("home"))


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
