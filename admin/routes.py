from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    jsonify,
)
from database.db import get_db
from psycopg2.extras import RealDictCursor


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


@admin_bp.route("/dashboard")
def dashboard():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # -------------------------
    # Admin Name
    # -------------------------
    cur.execute(
        """
        SELECT name
        FROM users
        WHERE user_id = %s
    """,
        (session["user_id"],),
    )

    admin = cur.fetchone()
    admin_name = admin["name"] if admin else "Admin"

    # -------------------------
    # Total Users
    # -------------------------
    cur.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
    """
    )

    total_users = cur.fetchone()["total"]

    # -------------------------
    # Active Projects
    # -------------------------
    cur.execute(
        """
    SELECT COUNT(*) AS total
    FROM projects
    WHERE status = 'ongoing'
      AND is_deleted = FALSE
    """
    )

    active_projects = cur.fetchone()["total"]

    # -------------------------
    # Overall Project Progress
    # -------------------------
    cur.execute(
        """
    SELECT
        ROUND(AVG(p.progress)) AS avg_progress
    FROM projects p

    JOIN users u
        ON p.leader_id = u.user_id

    WHERE
        p.is_deleted = FALSE
        AND u.role = 'project_leader'
    """
    )

    project_data = cur.fetchone()

    Overall_project_progress = (
        project_data["avg_progress"] if project_data["avg_progress"] else 0
    )

    # -------------------------
    # Overdue Projects
    # -------------------------
    cur.execute(
        """
    SELECT COUNT(*) AS total
    FROM projects
    WHERE status != 'completed'
      AND end_date < NOW()
      AND is_deleted = FALSE
    """
    )

    overdue_projects = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return render_template(
        "section/dashboard.html",
        admin_name=admin_name,
        total_users=total_users,
        active_projects=active_projects,
        Overall_project_progress=Overall_project_progress,
        overdue_projects=overdue_projects,
    )


######project overview used in dashboard this api calling by js
@admin_bp.route("/api/project-status")
def project_status_api():

    conn = get_db()
    cur = conn.cursor()

    # ---------------- Status Count ----------------

    cur.execute(
        """
    SELECT status, COUNT(*)
    FROM projects
    WHERE is_deleted = FALSE
    GROUP BY status
    """
    )

    status_rows = cur.fetchall()

    status_data = []

    for row in status_rows:
        status_data.append({"status": row[0], "total": row[1]})

    # ---------------- Trend (Per Project) ----------------

    cur.execute(
        """
    SELECT
        project_name,
        TO_CHAR(created_at, 'YYYY-MM') AS month,
        progress
    FROM projects
    WHERE is_deleted = FALSE
    ORDER BY created_at
    """
    )

    trend_rows = cur.fetchall()

    trend_data = {}

    for row in trend_rows:

        name = row[0]
        month = row[1]
        progress = int(row[2])

        if name not in trend_data:
            trend_data[name] = []

        trend_data[name].append({"month": month, "progress": progress})

    # ---------------- Deadline ----------------

    cur.execute(
        """
        SELECT project_name, progress
        FROM projects
        WHERE is_deleted = FALSE
        AND end_date IS NOT NULL
        ORDER BY end_date ASC
        LIMIT 6
        """
    )

    deadline_rows = cur.fetchall()

    deadline_data = []

    for row in deadline_rows:
        deadline_data.append({"project_name": row[0], "progress": row[1]})

    # ---------------- Creation Rate ----------------

    cur.execute(
        """
    SELECT TO_CHAR(created_at, 'YYYY-MM') AS month,
           COUNT(*) AS total
    FROM projects
    WHERE is_deleted = FALSE
    GROUP BY month
    ORDER BY month
    """
    )

    creation_rows = cur.fetchall()

    creation_data = []

    for row in creation_rows:
        creation_data.append({"month": row[0], "total": row[1]})

    cur.close()
    conn.close()

    return jsonify(
        {
            "status": status_data,
            "trend": trend_data,
            "deadline": deadline_data,
            "creation": creation_data,
        }
    )


# /************* 3 section used in dashboard
@admin_bp.route("/api/risk-projects")
def risk_projects_api():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
    SELECT project_name, progress, end_date
    FROM projects
    WHERE progress < 40
      AND end_date < NOW() + INTERVAL '7 days'
      AND is_deleted = FALSE
    """
    )

    risks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(risks)


@admin_bp.route("/api/recent-projects")
def recent_projects_api():

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
    SELECT project_name, status, progress, end_date
    FROM projects
    WHERE is_deleted = FALSE
    ORDER BY created_at DESC
    LIMIT 5
    """
    )

    projects = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(projects)


@admin_bp.route("/projects", methods=["GET", "POST"])
def projects():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # =====================
    # POST → ADD PROJECT
    # =====================
    if request.method == "POST":

        project_name = request.form.get("project_name")
        leader_id = request.form.get("leader_id")
        status = request.form.get("status")
        progress = request.form.get("progress") or 0
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        description = request.form.get("description")

        # Allow NULL leader
        leader_id = leader_id if leader_id else None

        # Validation
        if not project_name:
            return redirect(url_for("admin.projects"))

        cur.execute(
            """
            INSERT INTO projects
            (
                project_name,
                leader_id,
                status,
                progress,
                start_date,
                end_date,
                features,
                created_by,
                created_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                project_name,
                leader_id,
                status,
                progress,
                start_date,
                end_date,
                description,
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

    # ---------------------
    # Projects List
    # ---------------------
    cur.execute(
        """
    SELECT
        p.project_id,
        p.project_name,
        p.status,
        p.progress,
        p.start_date,
        p.end_date,
        p.features,
        p.leader_id,
        u.name AS leader_name,

        COUNT(pm.user_id) AS member_count

    FROM projects p

    LEFT JOIN users u
        ON p.leader_id = u.user_id

    LEFT JOIN project_members pm
        ON p.project_id = pm.project_id

    WHERE p.is_deleted = FALSE

    GROUP BY
        p.project_id,
        p.leader_id,
        u.name

    ORDER BY p.created_at DESC
    """
    )

    projects = cur.fetchall()

    # ---------------------
    # Free Leaders (Dropdown)
    # ---------------------
    cur.execute(
        """
        SELECT u.user_id, u.name
        FROM users u

        WHERE u.role = 'project_leader'
        AND u.is_active = TRUE
        AND u.is_registered = TRUE

        AND u.user_id NOT IN (

            SELECT leader_id
            FROM projects
            WHERE leader_id IS NOT NULL
                AND status IN ('ongoing','planning','on_hold')
                AND is_deleted = FALSE
        )

        ORDER BY u.name
        """
    )

    leaders = cur.fetchall()

    # =====================
    # PROJECT COUNTS
    # =====================

    # Total Projects
    cur.execute("SELECT COUNT(*) FROM projects WHERE is_deleted = FALSE")
    total_projects = cur.fetchone()["count"]

    # Ongoing
    cur.execute(
        "SELECT COUNT(*) FROM projects WHERE status='ongoing' AND is_deleted=FALSE "
    )
    ongoing = cur.fetchone()["count"]

    # Completed
    cur.execute(
        "SELECT COUNT(*) FROM projects WHERE status='completed' AND is_deleted=FALSE "
    )
    completed = cur.fetchone()["count"]

    # Planning
    cur.execute(
        "SELECT COUNT(*) FROM projects WHERE status='planning' AND is_deleted=FALSE"
    )
    planning = cur.fetchone()["count"]

    # Unassigned Projects
    cur.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE leader_id IS NULL
            AND is_deleted = FALSE
    """
    )
    unassigned_projects = cur.fetchone()["count"]

    # =====================
    # LEADER COUNTS
    # =====================

    # Total Leaders
    cur.execute(
        """
        SELECT COUNT(*)
        FROM users
        WHERE role='project_leader'
        AND is_active=TRUE
        AND is_registered=TRUE
    """
    )
    total_leaders = cur.fetchone()["count"]

    # Assigned Leaders
    cur.execute(
        """
    SELECT COUNT(DISTINCT leader_id)
    FROM projects
    WHERE leader_id IS NOT NULL
      AND status IN ('ongoing','planning','on_hold')
      AND is_deleted = FALSE
    """
    )
    assigned_leaders = cur.fetchone()["count"]

    # Free Leaders
    free_leaders = total_leaders - assigned_leaders

    # =====================
    # CLOSE DB
    # =====================
    cur.close()
    conn.close()

    # =====================
    # RENDER
    # =====================
    return render_template(
        "section/projects.html",
        projects=projects,
        leaders=leaders,
        # Project Stats
        total_count=total_projects,
        ongoing_count=ongoing,
        completed_count=completed,
        planning_count=planning,
        unassigned_projects=unassigned_projects,
        # Leader Stats
        total_leaders=total_leaders,
        assigned_leaders=assigned_leaders,
        free_leaders=free_leaders,
    )


@admin_bp.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
# js will pass url like this: http://127.0.0.1:5000/admin/projects/edit/projectid(eg., 1,2,5,18,...)
def edit_project(project_id):

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # =====================
    # Fetch ACTIVE project
    # =====================
    cur.execute(
        """
        SELECT *
        FROM projects
        WHERE project_id = %s
        AND is_deleted = FALSE
    """,
        (project_id,),
    )

    project = cur.fetchone()

    if not project:
        cur.close()
        conn.close()
        return "Project not found or deleted ❌"

    # =====================
    # Fetch FREE Leaders
    # (Except leaders assigned to other projects)
    # =====================
    cur.execute(
        """
        SELECT user_id, name
        FROM users
        WHERE role = 'leader'
        AND is_active = TRUE
        AND user_id NOT IN (
            SELECT leader_id
            FROM projects
            WHERE project_id != %s
            AND leader_id IS NOT NULL
            AND is_deleted = FALSE
        )
    """,
        (project_id,),
    )

    free_leaders = cur.fetchall()

    # =====================
    # UPDATE PROJECT
    # =====================
    if request.method == "POST":

        name = request.form.get("project_name")
        status = request.form.get("status")
        progress = request.form.get("progress") or 0
        end_date = request.form.get("end_date")
        description = request.form.get("description")
        leader_id = request.form.get("leader_id")  # 👈 NEW

        cur.execute(
            """
            UPDATE projects
            SET
                project_name = %s,
                status = %s,
                progress = %s,
                end_date = %s,
                features = %s,
                leader_id = %s,
                updated_at = NOW()
            WHERE project_id = %s
            AND is_deleted = FALSE
        """,
            (name, status, progress, end_date, description, leader_id, project_id),
        )
# If project marked as completed → free all members
        if status == "completed":
            cur.execute("""
        UPDATE project_members
        SET is_deleted = TRUE
        WHERE project_id = %s
    """, (project_id,))

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("admin.projects"))

    cur.close()
    conn.close()

    return render_template(
        "section/edit_project.html", project=project, free_leaders=free_leaders
    )


@admin_bp.route("/projects/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    # =====================
    # SOFT DELETE
    # =====================
    cur.execute(
        """
        UPDATE projects
        SET
            is_deleted = TRUE,
            updated_at = NOW()
        WHERE project_id = %s
        """,
        (project_id,),
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("admin.projects"))


# # ============================
# # PROJECTS (GET + POST)
# # ============================
# @admin_bp.route("/projects", methods=["GET", "POST"])
# def projects():

#     if not admin_login_required():
#         return redirect(url_for("auth.login"))

#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     # =====================
#     # POST → ADD PROJECT
#     # =====================
#     if request.method == "POST":

#         project_name = request.form.get("project_name")
#         leader_id = request.form.get("leader_id")
#         status = request.form.get("status")
#         progress = request.form.get("progress") or 0
#         start_date = request.form.get("start_date")
#         end_date = request.form.get("end_date")
#         description = request.form.get("description")

#         leader_id = leader_id if leader_id else None

#         # Validation
#         if not project_name:
#             return redirect(url_for("admin.projects"))

#         cur.execute(
#             """
#             INSERT INTO projects
#             (
#                 project_name,
#                 leader_id,
#                 status,
#                 progress,
#                 start_date,
#                 end_date,
#                 features,
#                 created_by,
#                 created_at
#             )
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
#             """,
#             (
#                 project_name,
#                 leader_id,
#                 status,
#                 progress,
#                 start_date,
#                 end_date,
#                 description,
#                 session["user_id"],
#             ),
#         )

#         conn.commit()

#         cur.close()
#         conn.close()

#         return redirect(url_for("admin.projects"))

#     # =====================
#     # GET → LOAD PAGE
#     # =====================

#     # Fetch projects
#     cur.execute(
#         """
#         SELECT
#             p.project_id,
#             p.project_name,
#             p.status,
#             p.progress,
#             p.start_date,
#             p.end_date,
#             p.features,
#             u.name AS leader_name,

#             COUNT(pm.user_id) AS member_count

#         FROM projects p

#         LEFT JOIN users u
#             ON p.leader_id = u.user_id

#         LEFT JOIN project_members pm
#             ON p.project_id = pm.project_id

#         GROUP BY
#             p.project_id,
#             u.name

#         ORDER BY p.created_at DESC
#     """
#     )

#     projects = cur.fetchall()

#     # Fetch only FREE + ACTIVE + REGISTERED leaders
#     cur.execute(
#         """
#         SELECT u.user_id, u.name
#         FROM users u
#         WHERE u.role = 'project_leader'
#         AND u.is_active = TRUE
#         AND u.is_registered = TRUE
#         AND u.user_id NOT IN (

#             SELECT leader_id
#             FROM projects
#             WHERE leader_id IS NOT NULL
#             AND status IN ('ongoing', 'planning', 'on_hold')

#         )
#         ORDER BY u.name
#     """
#     )

#     leaders = cur.fetchall()

#     # Fetch counts
#     cur.execute("SELECT COUNT(*) FROM projects")
#     total = cur.fetchone()["count"]

#     cur.execute("SELECT COUNT(*) FROM projects WHERE status='ongoing'")
#     ongoing = cur.fetchone()["count"]

#     cur.execute("SELECT COUNT(*) FROM projects WHERE status='completed'")
#     completed = cur.fetchone()["count"]

#     cur.execute("SELECT COUNT(*) FROM projects WHERE status='on_hold'")
#     onhold = cur.fetchone()["count"]

#     cur.execute("SELECT COUNT(*) FROM projects WHERE status='planning'")
#     planning = cur.fetchone()["count"]

#     cur.close()
#     conn.close()

#     return render_template(
#         "section/projects.html",
#         projects=projects,
#         leaders=leaders,
#         total_count=total,
#         ongoing_count=ongoing,
#         completed_count=completed,
#         onhold_count=onhold,
#         planning_count=planning,
#     )


# ============================
# EMPLOYEES
# ============================
@admin_bp.route("/employees", methods=["GET", "POST"])
def employees():

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # ============================
    # POST → ADD EMPLOYEE
    # ============================
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        designation = request.form.get("designation")
        role = request.form.get("role")
        status = request.form.get("status")

        is_active = True if status == "1" else False

        # Basic validation
        if not name or not email or not role:
            return redirect(url_for("admin.employees"))

        # Insert user
        cur.execute(
            """
            INSERT INTO users
            (name, email, role, designation, is_active, created_at)

            VALUES (%s,%s,%s,%s,%s,NOW())
            """,
            (name, email, role, designation, is_active),
        )

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("admin.employees"))

    # ============================
    # GET → FETCH EMPLOYEES
    # ============================

    # Fetch employees + project name
    cur.execute(
        """
    SELECT
        u.user_id,
        u.name,
        u.email,
        u.designation,
        u.role,
        u.is_active,
        u.created_at,

        (
            SELECT p.project_name
            FROM project_members pm
            JOIN projects p
                ON pm.project_id = p.project_id
            WHERE pm.user_id = u.user_id
              AND p.status IN ('ongoing','planning')
              AND p.is_deleted = FALSE
            LIMIT 1
        ) AS project_name

    FROM users u

    WHERE u.role != 'admin'

    ORDER BY u.created_at DESC
    """
    )

    employees = cur.fetchall()

    # ============================
    # STATS
    # ============================

    # Total employees
    cur.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE role != 'admin'
    """
    )

    total_employees = cur.fetchone()["total"]

    # Active employees
    cur.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE role != 'admin'
        AND is_active = TRUE
    """
    )

    active_employees = cur.fetchone()["total"]

    # New this month
    cur.execute(
        """
        SELECT COUNT(*) AS total
        FROM users
        WHERE role != 'admin'
        AND DATE_TRUNC('month', created_at) =
            DATE_TRUNC('month', CURRENT_DATE)
    """
    )

    new_employees = cur.fetchone()["total"]

    # ============================
    # DEPARTMENTS (DESIGNATION)
    # ============================

    cur.execute(
        """
        SELECT DISTINCT designation
        FROM users
        WHERE designation IS NOT NULL
    """
    )

    rows = cur.fetchall()

    departments = [row["designation"] for row in rows]

    cur.close()
    conn.close()

    return render_template(
        "section/manage_emp.html",
        employees=employees,
        total_employees=total_employees,
        active_employees=active_employees,
        new_employees=new_employees,
        departments=departments,
    )


@admin_bp.route("/employee/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch employee
    cur.execute(
        """
        SELECT user_id, name, email, designation, role, is_active
        FROM users
        WHERE user_id = %s
    """,
        (id,),
    )

    employee = cur.fetchone()

    if not employee:
        cur.close()
        conn.close()
        return "Employee Not Found ❌"

    # Update employee
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        designation = request.form.get("designation")
        role = request.form.get("role")
        status = request.form.get("status")

        is_active = True if status == "1" else False

        cur.execute(
            """
            UPDATE users
            SET name=%s,
                email=%s,
                designation=%s,
                role=%s,
                is_active=%s
            WHERE user_id=%s
        """,
            (name, email, designation, role, is_active, id),
        )

        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("admin.employees"))

    cur.close()
    conn.close()

    return render_template("admin/section/edit_employee.html", emp=employee)


@admin_bp.route("/employee/delete/<int:id>")
def delete_employee(id):

    if not admin_login_required():
        return redirect(url_for("auth.login"))

    conn = get_db()
    cur = conn.cursor()

    # Prevent deleting admin
    cur.execute(
        """
        SELECT role FROM users
        WHERE user_id = %s
    """,
        (id,),
    )

    user = cur.fetchone()

    if user and user[0] == "admin":
        cur.close()
        conn.close()
        return "Cannot delete Admin ❌"

    # Delete employee
    cur.execute(
        """
        DELETE FROM users
        WHERE user_id = %s
    """,
        (id,),
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("admin.employees"))


# ============================
# PROFILE
# ============================
@admin_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Access Denied ❌"}), 403

    user_id = session["user_id"]

    conn = None
    cur = None

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # =============================
        # POST → UPDATE PROFILE
        # =============================
        if request.method == "POST":

            name = request.form.get("name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            bio = request.form.get("bio")

            cur.execute(
                """
                UPDATE users
                SET name=%s,
                    email=%s
                WHERE user_id=%s
                """,
                (name, email, user_id),
            )

            conn.commit()

            return jsonify(
                {"status": "success", "message": "Profile updated successfully ✅"}
            )

        # =============================
        # GET → FETCH DATA
        # =============================
        cur.execute(
            """
            SELECT name, email, role
            FROM users
            WHERE user_id=%s
            """,
            (user_id,),
        )

        user = cur.fetchone()

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

        return render_template("section/profile.html", user=user, logs=logs)

    except Exception as e:

        if conn:
            conn.rollback()

        print("Profile Route Error:", e)

        return jsonify({"status": "error", "message": "Something went wrong ❌"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
