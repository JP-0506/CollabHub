from flask import Flask, render_template, redirect, session, url_for

from auth import auth_bp
from admin import admin_bp

app = Flask(__name__)

app.secret_key = "collabhub_secret_key"


# -----------------------------
# Register Blueprints
# -----------------------------
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -----------------------------
# LEADER DASHBOARD
# -----------------------------
@app.route("/projectleader/dashboard")
def leader_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "project_leader":
        return "Access Denied ❌"

    return render_template("projectleader/dashboard.html")


# -----------------------------
# EMPLOYEE DASHBOARD
# -----------------------------
@app.route("/employee/dashboard")
def employee_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "employee":
        return "Access Denied ❌"

    return render_template("employee/dashboard.html")


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
