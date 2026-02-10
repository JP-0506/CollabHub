from flask import Blueprint, render_template, session, jsonify
from database.db import get_db

project_leader_bp = Blueprint("project_leader", __name__)

@project_leader_bp.route("/my-team")
def my_team():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})

    leader_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.emp_id, e.name, e.email
        FROM employees e
        JOIN project_assignments p
        ON e.emp_id = p.emp_id
        WHERE p.leader_id = %s
    """, (leader_id,))

    team = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(team)

@project_leader_bp.route("/myproject")
def my_project():
    return render_template("projectLeader/myproject.html")

@project_leader_bp.route("/tasks")
def tasks():
    return render_template("projectLeader/tasks.html")

@project_leader_bp.route("/reports")
def reports():
    return render_template("projectLeader/reports.html")

@project_leader_bp.route("/my_profile")
def my_profile():
    return render_template("projectLeader/my_profile.html")

@project_leader_bp.route("/my_team")
def my_team_page():
    return render_template("projectLeader/my_team.html")

@project_leader_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})
    
    if session.get("role") != "project_leader":
        return "Access Denied ❌"
    
    return render_template("projectLeader/dashboard.html")