from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
)
from database.db import get_db

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


# ============================
# LOGIN CHECK HELPER
# ============================
def admin_login_required():

    if "user_id" not in session:
        return False

    if session.get("role") != "admin":
        return False

    return True


# ============================
# ADMIN HOME
# ============================
@admin_bp.route("/")
def admin_home():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    return render_template("admin.html")


# ============================
# DASHBOARD
# ============================
@admin_bp.route("/dashboard")
def dashboard():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    return render_template("section/dashboard.html")


# ============================
# PROJECTS (GET + POST)
# ============================
@admin_bp.route("/projects", methods=["GET", "POST"])
def projects():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    # =====================
    # POST → ADD PROJECT
    # =====================
    if request.method == "POST":

        project_name = request.form.get("project_name")
        leader_id = request.form.get("leader_id")
        status = request.form.get("status")
        progress = request.form.get("progress")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not project_name or not status:

            return redirect(url_for("admin.projects"))

        cur.execute(
            """
            INSERT INTO projects
            (project_name, leader_id, status, progress,
             start_date, end_date, created_by, created_at)

            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                project_name,
                leader_id,
                status,
                progress,
                start_date,
                end_date,
                session["user_id"],
            ),
        )

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("admin.projects"))

    # =====================
    # GET → LOAD PAGE
    # =====================

    # Fetch projects
    cur.execute(
        """
        SELECT
            p.project_id,
            p.project_name,
            p.status,
            p.progress,
            p.start_date,
            p.end_date,
            u.name AS leader_name
        FROM projects p
        LEFT JOIN users u
        ON p.leader_id = u.user_id
        ORDER BY p.created_at DESC
        """
    )

    projects = cur.fetchall()

    # Fetch leaders
    cur.execute(
        """
        SELECT user_id, name
        FROM users
        WHERE role = 'project_leader'
        """
    )

    leaders = cur.fetchall()

    # Fetch counts
    cur.execute("SELECT COUNT(*) FROM projects")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects WHERE status='ongoing'")
    ongoing = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects WHERE status='completed'")
    completed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects WHERE status='on_hold'")
    onhold = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM projects WHERE status='planning'")
    planning = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "section/projects.html",
        projects=projects,
        leaders=leaders,
        total_count=total,
        ongoing_count=ongoing,
        completed_count=completed,
        onhold_count=onhold,
        planning_count=planning,  # ✅ add this
    )


# ============================
# EMPLOYEES
# ============================
@admin_bp.route("/employees")
def employees():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    return render_template("section/manage_emp.html")


# ============================
# ASSIGN LEADER
# ============================
@admin_bp.route("/assign-leader")
def assign_leader():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    return render_template("section/assign_leader.html")


# ============================
# PROFILE
# ============================
@admin_bp.route("/profile")
@admin_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return "Access Denied ❌"

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    # --------------------
    # UPDATE PROFILE
    # --------------------
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        bio = request.form.get("bio")

        cur.execute(
            """
            UPDATE users
            SET name=%s, email=%s
            WHERE user_id=%s
        """,
            (name, email, user_id),
        )

        conn.commit()

    # --------------------
    # FETCH USER
    # --------------------
    cur.execute(
        """
        SELECT name, email, role
        FROM users
        WHERE user_id=%s
    """,
        (user_id,),
    )

    user = cur.fetchone()

    # --------------------
    # LOGIN LOGS
    # --------------------
    cur.execute(
        """
        SELECT login_time, ip_address
        FROM login_logs
        WHERE user_id=%s
        ORDER BY login_time DESC
        LIMIT 5
    """,
        (user_id,),
    )

    logs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("section/profile.html", user=user, logs=logs)
