from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
from database.db import get_db
from psycopg2.extras import RealDictCursor
from DS.TaskPriorityQueue import TaskPriorityQueue

employee_bp = Blueprint("employee", __name__)


# ============================
# LOGIN CHECK HELPER (LIKE ADMIN)
# ============================
def employee_login_required():
    if "user_id" not in session:
        return False
    if session.get("role") != "employee":
        return False
    # STRICT: username must exist
    if "username" not in session or not session.get("username"):
        return False
    return True


# ============================
# HOME
# ============================
@employee_bp.route("/")
def employee_home():
    if not employee_login_required():
        return redirect(url_for("auth.login"))
    return redirect(url_for("employee.dashboard"))


# ============================
# DASHBOARD
# ============================
@employee_bp.route("/dashboard")
def dashboard():
    if not employee_login_required():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # -----------------------------
    # User Info
    # -----------------------------
    cur.execute(
        """
        SELECT name, email, role
        FROM users
        WHERE user_id = %s
    """,
        (user_id,),
    )
    user = cur.fetchone() or {}

    # ==========================================================
    # IMPORTANT:
    # This assumes tasks table has: tasks.project_id
    # ==========================================================

    # -----------------------------
    # Task Stats (ONLY non-deleted projects)
    # -----------------------------
    cur.execute(
        """
        SELECT
            COUNT(*) AS total_tasks,
            COUNT(*) FILTER (WHERE t.status = 'completed') AS completed_tasks,
            COUNT(*) FILTER (WHERE t.status = 'in_progress') AS in_progress_tasks,
            COUNT(*) FILTER (WHERE t.status = 'todo') AS todo_tasks
        FROM tasks t
        JOIN projects p ON p.project_id = t.project_id
        WHERE t.assigned_to = %s
          AND p.is_deleted = FALSE
    """,
        (user_id,),
    )
    stats = cur.fetchone() or {}

    # -----------------------------
    # Project Count (ONLY non-deleted projects)
    # -----------------------------
    cur.execute(
        """
        SELECT COUNT(DISTINCT pm.project_id) AS project_count
        FROM project_members pm
        JOIN projects p ON p.project_id = pm.project_id
        WHERE pm.user_id = %s
          AND p.is_deleted = FALSE
    """,
        (user_id,),
    )
    project_count = (cur.fetchone() or {}).get("project_count", 0) or 0

    # -----------------------------
    # Weekly Completed Tasks (ONLY non-deleted projects)
    # -----------------------------
    cur.execute(
        """
        SELECT
            EXTRACT(DOW FROM t.due_date) AS dow,
            COUNT(*) FILTER (WHERE t.status = 'completed') AS completed_count
        FROM tasks t
        JOIN projects p ON p.project_id = t.project_id
        WHERE t.assigned_to = %s
          AND t.due_date IS NOT NULL
          AND p.is_deleted = FALSE
        GROUP BY dow
        ORDER BY dow
    """,
        (user_id,),
    )
    weekly_db_data = cur.fetchall() or []

    week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    weekly_dict = {
        int(r["dow"]): (r["completed_count"] or 0)
        for r in weekly_db_data
        if r.get("dow") is not None
    }

    weekly_labels = week_days
    weekly_values = [weekly_dict.get(i, 0) for i in range(7)]

    cur.close()
    conn.close()

    return render_template(
        "employees/employee_dashboard.html",
        user=user,
        total_tasks=stats.get("total_tasks", 0) or 0,
        completed_tasks=stats.get("completed_tasks", 0) or 0,
        in_progress_tasks=stats.get("in_progress_tasks", 0) or 0,
        todo_tasks=stats.get("todo_tasks", 0) or 0,
        project_count=project_count,
        weekly_labels=weekly_labels,
        weekly_values=weekly_values,
        active_page="dashboard",
    )


# ============================
# MY WORK
# ============================
@employee_bp.route("/my-work")
def my_work():
    if not employee_login_required():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ✅ Fetch assigned project info
    cur.execute(
        """
    SELECT 
        p.project_id,
        p.project_name,
        p.features,
        p.status
    FROM projects p
    JOIN project_members pm ON p.project_id = pm.project_id
    WHERE pm.user_id = %s
    AND p.is_deleted = FALSE
    AND pm.is_deleted = FALSE
    LIMIT 1
    """,
        (user_id,),
    )
    project = cur.fetchone()

    cur.execute(
        """
    SELECT 
        t.task_id,
        t.title,
        t.status,
        t.priority,
        t.due_date
    FROM tasks t
    JOIN projects p ON t.project_id = p.project_id
    WHERE t.assigned_to = %s
    AND p.is_deleted = FALSE   -- 🔥 hide deleted project tasks
    ORDER BY t.due_date ASC NULLS LAST
    """,
        (user_id,),
    )
    raw_tasks = cur.fetchall() or []

    # 🔢 Apply Priority Queue — sort tasks: high → medium → low
    pq = TaskPriorityQueue()
    pq.push_all(raw_tasks)
    tasks = pq.get_all()

    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    cur.close()
    conn.close()

    return render_template(
        "employees/employee_work.html",
        project=project,
        tasks=tasks,
        progress=progress,
        active_page="work",
    )


# ============================
# SUBMIT TASK FOR REVIEW (instead of complete)
# ============================
@employee_bp.route("/submit-task/<int:task_id>", methods=["POST"])
def submit_task(task_id):
    # For fetch() APIs return JSON, don't redirect
    if not employee_login_required():
        return jsonify({"success": False, "message": "Not logged in"}), 401

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    # Check current status first
    cur.execute(
        """
        SELECT status FROM tasks 
        WHERE task_id = %s AND assigned_to = %s
    """,
        (task_id, user_id),
    )

    task = cur.fetchone()
    if not task:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Task not found"}), 404

    if task[0] == "submitted":
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Task already submitted"}), 400

    if task[0] == "approved":
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Task already approved"}), 400

    # Update to submitted status
    cur.execute(
        """
        UPDATE tasks
        SET status = 'submitted', 
            submitted_at = CURRENT_TIMESTAMP,
            last_action_by = %s,
            last_action_at = CURRENT_TIMESTAMP
        WHERE task_id = %s AND assigned_to = %s
    """,
        (user_id, task_id, user_id),
    )

    conn.commit()
    updated = cur.rowcount

    cur.close()
    conn.close()

    if updated == 0:
        return (
            jsonify({"success": False, "message": "Task not found / not allowed"}),
            403,
        )

    return jsonify({"success": True, "message": "Task submitted for review"})


# ============================
# PROFILE
# ============================
@employee_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if not employee_login_required():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()

        # update ONLY name & email
        cur.execute(
            """
            UPDATE users
            SET name=%s, email=%s, updated_at=CURRENT_TIMESTAMP
            WHERE user_id=%s
        """,
            (name, email, user_id),
        )
        conn.commit()

        # keep sidebar name updated
        if name:
            session["username"] = name

        return redirect(url_for("employee.profile"))

    cur.execute(
        """
        SELECT name, email, role, designation, avatar
        FROM users
        WHERE user_id = %s
    """,
        (user_id,),
    )
    user = cur.fetchone() or {}

    cur.close()
    conn.close()

    return render_template(
        "employees/employee_profile.html", user=user, active_page="profile"
    )


# ============================
# Change Password(In profile)
# ============================


@employee_bp.route("/change-password", methods=["POST"])
def change_password():
    if not employee_login_required():
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json(silent=True) or {}
    current_password = (data.get("current_password") or "").strip()
    new_password = (data.get("new_password") or "").strip()
    confirm_password = (data.get("confirm_password") or "").strip()

    if not current_password or not new_password or not confirm_password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    if len(new_password) < 8:
        return (
            jsonify(
                {"success": False, "message": "Password must be at least 8 characters"}
            ),
            400,
        )

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT password_hash FROM auth WHERE user_id=%s", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Auth record not found"}), 404

    if row[0] != current_password:
        cur.close()
        conn.close()
        return jsonify({"success": False, "message": "Current password is wrong"}), 400

    cur.execute(
        """
        UPDATE auth
        SET password_hash=%s, updated_at=CURRENT_TIMESTAMP
        WHERE user_id=%s
    """,
        (new_password, user_id),
    )
    conn.commit()

    cur.close()
    conn.close()
    return (
        jsonify({"success": True, "message": "Password changed successfully ✅"}),
        200,
    )


# ============================
# TEAM
# ============================
@employee_bp.route("/team")
def my_team():
    if not employee_login_required():
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ✅ Only take project_ids that are NOT deleted
    cur.execute(
        """
        SELECT pm.project_id
        FROM project_members pm
        JOIN projects p ON pm.project_id = p.project_id
        WHERE pm.user_id = %s
          AND p.is_deleted = FALSE
          AND pm.is_deleted = FALSE
    """,
        (user_id,),
    )
    project_ids = [row["project_id"] for row in (cur.fetchall() or [])]

    if not project_ids:
        cur.close()
        conn.close()
        return render_template(
            "employees/employee_team.html", team_members=[], active_page="team"
        )

    # ✅ Also ensure members come only from NOT deleted projects
    cur.execute(
        """
        SELECT u.user_id, u.name, u.email, u.designation, u.avatar,
               pm.role_in_project, pm.project_id
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE pm.project_id = ANY(%s)
          AND p.is_deleted = FALSE
          AND pm.is_deleted = FALSE
        ORDER BY pm.project_id, u.name
    """,
        (project_ids,),
    )
    team_members = cur.fetchall() or []

    cur.close()
    conn.close()

    return render_template(
        "employees/employee_team.html", team_members=team_members, active_page="team"
    )
