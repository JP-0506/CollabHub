from flask import (
    Blueprint,
    render_template,
    session,
    jsonify,
    request,
    redirect,
    url_for,
    make_response,
    current_app,
)
from database.db import get_db
from datetime import datetime, timedelta
import io
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from flask_mail import Mail, Message


project_leader_bp = Blueprint("project_leader", __name__)


# ============================
# HELPER FUNCTIONS
# ============================


def get_leader_project(leader_id, cur):
    """Get the leader's active project only. Returns None if closed or not found."""
    cur.execute(
        """
        SELECT p.project_id, p.project_name
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY p.created_at DESC
        LIMIT 1
    """,
        (leader_id, leader_id),
    )
    return cur.fetchone()


def get_notifications(leader_id, cur):
    """Fetch notification count and recent 3 notifications for a leader."""
    cur.execute(
        """
        SELECT COUNT(*) 
        FROM notifications 
        WHERE receiver_id = %s AND is_read = false
    """,
        (leader_id,),
    )
    notification_count = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT n.message, n.sent_at, u.name as sender_name
        FROM notifications n
        JOIN users u ON n.sender_id = u.user_id
        WHERE n.receiver_id = %s AND n.is_read = false
        ORDER BY n.sent_at DESC
        LIMIT 3
    """,
        (leader_id,),
    )
    notifications = cur.fetchall()

    recent_notifications = [
        {
            "message": notif[0],
            "sent_at": notif[1],  # raw datetime or None
            "sender_name": notif[2],
        }
        for notif in notifications
    ]
    return notification_count, recent_notifications


def generate_pdf_report(
    project,
    stats,
    team_data,
    tasks_by_status=None,
    tasks_by_priority=None,
    recent_activities=None,
    completion_rate=0,
):
    """Generate a PDF report and return the buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor("#2563eb"),
    )

    story.append(Paragraph(f"Project Report: {project[1]}", title_style))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 20))

    # Task Statistics
    story.append(Paragraph("Task Statistics", styles["Heading2"]))
    story.append(Spacer(1, 10))

    stats_data = [
        ["Metric", "Count"],
        ["Total Tasks", str(stats[0] or 0)],
        ["Completed", str(stats[1] or 0)],
        ["In Progress", str(stats[2] or 0)],
        ["Pending Review", str(stats[3] or 0)],
        ["Overdue", str(stats[4] or 0)],
        ["Completion Rate", f"{completion_rate}%"],
    ]
    stats_table = Table(stats_data)
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(stats_table)
    story.append(Spacer(1, 30))

    # Tasks by Status
    if tasks_by_status:
        story.append(Paragraph("Tasks by Status", styles["Heading2"]))
        story.append(Spacer(1, 10))
        status_data = [["Status", "Count"]] + [
            [s[0], str(s[1])] for s in tasks_by_status
        ]
        status_table = Table(status_data)
        status_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(status_table)
        story.append(Spacer(1, 30))

    # Tasks by Priority
    if tasks_by_priority:
        story.append(Paragraph("Tasks by Priority", styles["Heading2"]))
        story.append(Spacer(1, 10))
        priority_data = [["Priority", "Count"]] + [
            [p[0], str(p[1])] for p in tasks_by_priority
        ]
        priority_table = Table(priority_data)
        priority_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f59e0b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(priority_table)
        story.append(Spacer(1, 30))

    # Team Performance
    story.append(Paragraph("Team Performance", styles["Heading2"]))
    story.append(Spacer(1, 10))
    team_table_data = [["Name", "Role", "Tasks", "Completed", "Overdue"]]
    for member in team_data:
        team_table_data.append(
            [
                member[0],
                member[1] or "N/A",
                str(member[2] or 0),
                str(member[3] or 0),
                str(member[4] or 0) if len(member) > 4 else "0",
            ]
        )
    team_table = Table(team_table_data)
    team_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8b5cf6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(team_table)
    story.append(Spacer(1, 30))

    # Recent Activities
    if recent_activities:
        story.append(Paragraph("Recent Activities", styles["Heading2"]))
        story.append(Spacer(1, 10))
        activities_data = [["User", "Activity", "Date"]]
        for activity in recent_activities:
            desc = (
                f"Completed task: {activity[1]}"
                if activity[0] == "task_completed"
                else f"Joined as {activity[1]}"
            )
            activities_data.append(
                [
                    activity[2],
                    desc,
                    activity[3].strftime("%b %d, %Y") if activity[3] else "N/A",
                ]
            )
        activities_table = Table(activities_data)
        activities_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6b7280")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(activities_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


# ============================
# ROUTES
# ============================


@project_leader_bp.route("/my_team")
def my_team_page():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT u.user_id, u.name, u.email, u.designation, p.project_name, pm.role_in_project
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        AND u.role = 'employee'
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY u.name;
    """,
        (leader_id,),
    )
    team = cur.fetchall()

    task_counts = {}
    if team:
        user_ids = [member[0] for member in team]
        placeholders = ",".join(["%s"] * len(user_ids))
        cur.execute(
            f"""
            SELECT 
                assigned_to,
                COUNT(*) as total_tasks,
                COUNT(*) FILTER (WHERE status = 'approved') as completed_tasks
            FROM tasks
            WHERE assigned_to IN ({placeholders})
            GROUP BY assigned_to
        """,
            user_ids,
        )
        for result in cur.fetchall():
            task_counts[result[0]] = {"total": result[1], "completed": result[2]}

    total_members = len(team)
    completed_tasks = sum(c.get("completed", 0) for c in task_counts.values())
    avg_productivity = (
        round(completed_tasks / total_members, 1) if total_members > 0 else 0
    )

    cur.execute(
        """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE t.due_date >= CURRENT_DATE OR t.status = 'approved') as on_time_tasks
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s
    """,
        (leader_id,),
    )
    delivery_stats = cur.fetchone()
    on_time_rate = (
        round((delivery_stats[1] / delivery_stats[0] * 100), 1)
        if delivery_stats[0] > 0
        else 0
    )

    cur.execute(
        """
        SELECT p.project_id, p.project_name 
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY p.created_at DESC;
    """,
        (leader_id, leader_id),
    )
    leader_projects = cur.fetchall()

    cur.execute(
        """
        SELECT u.user_id, u.name, u.designation
        FROM users u
        WHERE u.role = 'employee' 
        AND u.user_id != %s
        AND NOT EXISTS (
            SELECT 1
            FROM project_members pm
            JOIN projects p ON pm.project_id = p.project_id
            WHERE pm.user_id = u.user_id
            AND p.status IN ('ongoing','planning','on_hold')
            AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        )
        ORDER BY u.name;
    """,
        (leader_id,),
    )
    available_employees = cur.fetchall()

    # to fetch past memeber
    cur.execute(
        """
        SELECT u.user_id, u.name, u.email, u.designation, pm.role_in_project, pm.joined_at
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        AND u.role = 'employee'
        AND pm.is_deleted = TRUE
        ORDER BY pm.joined_at DESC;
    """,
        (leader_id,),
    )
    past_members = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/my_team.html",
        team=team,
        task_counts=task_counts,
        leader_projects=leader_projects,
        available_employees=available_employees,
        total_members=total_members,
        avg_productivity=avg_productivity,
        on_time_rate=on_time_rate,
        active_now=0,
        past_members=past_members,
    )


@project_leader_bp.route("/myproject")
def my_project():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT p.project_id, p.project_name, p.features, p.status, p.start_date, p.end_date
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY p.created_at DESC
        LIMIT 1;
    """,
        (leader_id, leader_id),
    )
    project_row = cur.fetchone()

    if not project_row:
        return render_template(
            "projectLeader/projectDetails.html",
            project=None,
            tasks=[],
            employees=[],
            task_stats={},
        )

    project = {
        "project_id": project_row[0],
        "project_name": project_row[1],
        "features": project_row[2],
        "status": project_row[3],
        "start_date": project_row[4],
        "end_date": project_row[5],
    }
    project_id = project["project_id"]

    cur.execute(
        """
        SELECT t.task_id, t.title, t.description, t.status, t.priority, t.due_date, u.name
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = %s
        ORDER BY 
            CASE t.priority 
                WHEN 'High' THEN 1 
                WHEN 'Medium' THEN 2 
                WHEN 'Low' THEN 3 
            END,
            t.due_date ASC NULLS LAST;
    """,
        (project_id,),
    )
    tasks = [
        {
            "task_id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "due_date": row[5],
            "assigned_to_name": row[6],
        }
        for row in cur.fetchall()
    ]

    cur.execute(
        """
        SELECT u.user_id, u.name, u.email, pm.role_in_project
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        WHERE pm.project_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY u.name;
    """,
        (project_id,),
    )
    employees = [
        {"user_id": row[0], "name": row[1], "email": row[2], "role_in_project": row[3]}
        for row in cur.fetchall()
    ]

    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for t in tasks if t["status"] and t["status"].lower() == "completed"
    )
    task_stats = {
        "total": total_tasks,
        "completed": completed_tasks,
        "pending": total_tasks - completed_tasks,
        "progress": (
            int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        ),
    }

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/projectDetails.html",
        project=project,
        tasks=tasks,
        employees=employees,
        task_stats=task_stats,
        now=datetime.now().date(),
    )


@project_leader_bp.route("/tasks")
def tasks():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            t.task_id, t.title, t.description, t.priority, t.status,
            t.due_date, p.project_name, u.name AS assigned_to_name,
            t.rejection_reason, t.submitted_at
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        JOIN users u ON t.assigned_to = u.user_id
        WHERE p.leader_id = %s
        ORDER BY 
            CASE 
                WHEN t.status = 'submitted' THEN 1
                WHEN t.status = 'in_progress' THEN 2
                WHEN t.status = 'rejected' THEN 3
                ELSE 4
            END,
            t.created_at DESC;
    """,
        (leader_id,),
    )
    tasks = cur.fetchall()

    cur.execute(
        """
        SELECT 
            COUNT(*) FILTER (WHERE t.status = 'approved') as completed,
            COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'approved') as overdue,
            COUNT(*) FILTER (WHERE t.status = 'in_progress') as in_progress,
            COUNT(*) FILTER (WHERE t.status = 'submitted') as pending_review
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s;
    """,
        (leader_id,),
    )
    task_summary = cur.fetchone()

    cur.execute(
        """
        SELECT p.project_id, p.project_name 
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY p.created_at DESC;
    """,
        (leader_id, leader_id),
    )
    projects = cur.fetchall()

    cur.execute(
        """
        SELECT DISTINCT u.user_id, u.name
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY u.name;
    """,
        (leader_id,),
    )
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/tasks.html",
        tasks=tasks,
        projects=projects,
        users=users,
        task_summary=task_summary,
        now=datetime.now().date(),
    )


@project_leader_bp.route("/add_team_member", methods=["POST"])
def add_team_member():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    user_id = request.form["user_id"]
    role = request.form["role"]

    conn = get_db()
    cur = conn.cursor()

    project = get_leader_project(leader_id, cur)
    if not project:
        cur.close()
        conn.close()
        return (
            jsonify({"success": False, "error": "No project found for this leader"}),
            404,
        )

    # Check if project is closed
    cur.execute("SELECT status FROM projects WHERE project_id = %s", (project[0],))
    status = cur.fetchone()[0]
    if status == "closed":
        cur.close()
        conn.close()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Project is closed. Cannot add team members.",
                }
            ),
            400,
        )

    cur.execute(
        """
        INSERT INTO project_members (project_id, user_id, role_in_project, joined_at, is_deleted)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, FALSE)
        ON CONFLICT (project_id, user_id) 
        DO UPDATE SET 
            is_deleted = FALSE,
            role_in_project = EXCLUDED.role_in_project,
            joined_at = CURRENT_TIMESTAMP;
    """,
        (project[0], user_id, role),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Team member added successfully"})


@project_leader_bp.route("/reports")
def reports():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT p.project_id, p.project_name, p.start_date, p.end_date, p.status, p.progress
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY p.created_at DESC
        LIMIT 1;
    """,
        (leader_id, leader_id),
    )
    project = cur.fetchone()

    if not project:
        return render_template("projectLeader/reports.html", error="No project found")

    project_id = project[0]

    cur.execute(
        """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'approved') as completed_tasks,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress_tasks,
            COUNT(*) FILTER (WHERE status = 'Pending Review') as pending_review_tasks,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'approved') as overdue_tasks
        FROM tasks 
        WHERE project_id = %s;
    """,
        (project_id,),
    )
    task_stats = cur.fetchone()

    cur.execute(
        """
        SELECT COUNT(*) 
        FROM project_members 
        WHERE project_id = %s
        AND (is_deleted = FALSE OR is_deleted IS NULL);
    """,
        (project_id,),
    )
    team_count = cur.fetchone()[0]

    total_tasks = task_stats[0] or 0
    completed_tasks = task_stats[1] or 0
    completion_rate = (
        round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    )

    cur.execute(
        """
        SELECT 
            u.user_id, u.name, u.designation,
            COUNT(t.task_id) as total_assigned,
            COUNT(*) FILTER (WHERE t.status = 'approved') as tasks_completed,
            COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'approved') as overdue_tasks
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        GROUP BY u.user_id, u.name, u.designation
        ORDER BY tasks_completed DESC;
    """,
        (project_id,),
    )
    team_performance = cur.fetchall()

    cur.execute(
        """
        SELECT status, COUNT(*) 
        FROM tasks 
        WHERE project_id = %s 
        GROUP BY status;
    """,
        (project_id,),
    )
    tasks_by_status = cur.fetchall()

    cur.execute(
        """
        SELECT priority, COUNT(*) 
        FROM tasks 
        WHERE project_id = %s 
        GROUP BY priority;
    """,
        (project_id,),
    )
    tasks_by_priority = cur.fetchall()

    cur.execute(
        """
        (SELECT 
            'task_completed' as type, t.title as description,
            u.name as user_name, t.completed_at as created_at
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC LIMIT 5)
        UNION ALL
        (SELECT 
            'member_joined' as type, pm.role_in_project as description,
            u.name as user_name, pm.joined_at as created_at
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY pm.joined_at DESC LIMIT 5)
        ORDER BY created_at DESC LIMIT 10;
    """,
        (project_id, project_id),
    )
    recent_activities = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/reports.html",
        project=project,
        task_stats=task_stats,
        team_count=team_count,
        completion_rate=completion_rate,
        team_performance=team_performance,
        tasks_by_status=tasks_by_status,
        tasks_by_priority=tasks_by_priority,
        recent_activities=recent_activities,
    )


@project_leader_bp.route("/my_profile")
def my_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT user_id, name, email, role, designation, avatar, created_at
        FROM users 
        WHERE user_id = %s;
    """,
        (leader_id,),
    )
    user_data = cur.fetchone()

    if not user_data:
        cur.close()
        conn.close()
        return "User not found", 404

    cur.execute(
        """
        SELECT p.project_id, p.project_name, p.status, p.progress, p.start_date, p.end_date
        FROM projects p
        JOIN project_members pm ON p.project_id = pm.project_id
        WHERE p.leader_id = %s
        AND p.status != 'closed'
        AND p.is_deleted = FALSE
        AND pm.user_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY 
            CASE WHEN p.status != 'completed' THEN 1 ELSE 2 END,
            p.created_at DESC;
    """,
        (leader_id, leader_id),
    )
    projects = cur.fetchall()

    cur.execute(
        """
        SELECT 
            COUNT(DISTINCT pm.user_id) as team_size,
            COUNT(DISTINCT t.task_id) as total_tasks,
            COUNT(DISTINCT CASE WHEN t.status = 'approved' THEN t.task_id END) as completed_tasks
        FROM projects p
        LEFT JOIN project_members pm ON p.project_id = pm.project_id AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        LEFT JOIN tasks t ON p.project_id = t.project_id
        WHERE p.leader_id = %s;
    """,
        (leader_id,),
    )
    team_stats = cur.fetchone()

    notification_count, recent_notifications = get_notifications(leader_id, cur)

    cur.close()
    conn.close()

    user = {
        "user_id": user_data[0],
        "name": user_data[1],
        "email": user_data[2],
        "role": user_data[3],
        "designation": user_data[4] or "Project Leader",
        "avatar": user_data[5],
        "joining_date": user_data[6].strftime("%b %d, %Y") if user_data[6] else "N/A",
        "phone": "Not provided",
        "bio": "No bio available.",
        "profile_completion": 70,
    }

    project_list = [
        {
            "id": p[0],
            "name": p[1],
            "status": p[2] or "active",
            "progress": p[3] or 0,
            "start_date": p[4].strftime("%b %d, %Y") if p[4] else "N/A",
            "end_date": p[5].strftime("%b %d, %Y") if p[5] else "N/A",
        }
        for p in projects
    ]

    stats = {
        "team_size": team_stats[0] or 0,
        "total_tasks": team_stats[1] or 0,
        "completed_tasks": team_stats[2] or 0,
        "completion_rate": round((team_stats[2] or 0) / (team_stats[1] or 1) * 100, 1),
    }

    return render_template(
        "projectLeader/my_profile.html",
        user=user,
        projects=project_list,
        stats=stats,
        notification_count=notification_count,
        recent_notifications=recent_notifications,
    )


@project_leader_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})

    if session.get("role") != "project_leader":
        return "Access Denied ❌"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name FROM users WHERE user_id = %s;", (leader_id,))
    result = cur.fetchone()
    user_name = result[0] if result else "User"

    cur.execute(
        """
        SELECT COUNT(*) 
        FROM projects 
        WHERE leader_id = %s AND status NOT IN ('completed', 'closed') AND is_deleted = FALSE;
    """,
        (leader_id,),
    )
    active_projects = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT 
            COUNT(*) FILTER (WHERE t.status = 'approved') as completed_tasks,
            COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'approved') as overdue_tasks,
            COUNT(*) as total_tasks
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s;
    """,
        (leader_id,),
    )
    task_stats = cur.fetchone()
    completed_tasks = task_stats[0] or 0
    overdue_tasks = task_stats[1] or 0
    total_tasks = task_stats[2] or 0

    cur.execute(
        """
        SELECT COUNT(DISTINCT u.user_id)
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        AND u.role != 'project_leader';
    """,
        (leader_id,),
    )
    team_members = cur.fetchone()[0] or 0

    cur.execute(
        """
        SELECT 
            TO_CHAR(date_trunc('day', t.completed_at), 'Dy') as day,
            COUNT(*) as completed
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s 
            AND t.completed_at IS NOT NULL
            AND t.completed_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY date_trunc('day', t.completed_at)
        ORDER BY date_trunc('day', t.completed_at);
    """,
        (leader_id,),
    )
    weekly_data = cur.fetchall()

    today = datetime.now().date()
    chart_labels = []
    chart_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_name = day.strftime("%a")
        chart_labels.append(day_name)
        day_data = next((d[1] for d in weekly_data if d[0] == day_name), 0)
        chart_values.append(day_data)

    cur.execute(
        """
        (SELECT 
            'task_completed' as type, t.title as description,
            u.name as user_name, t.completed_at as created_at, p.project_name
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC LIMIT 4)
        UNION ALL
        (SELECT 
            'member_joined' as type, pm.role_in_project as description,
            u.name as user_name, pm.joined_at as created_at, p.project_name
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY pm.joined_at DESC LIMIT 4)
        ORDER BY created_at DESC LIMIT 8;
    """,
        (leader_id, leader_id),
    )
    activities = cur.fetchall()

    recent_activities = [
        {
            "type": a[0],
            "description": a[1],
            "user_name": a[2],
            "created_at": a[3],
            "project_name": a[4],
        }
        for a in activities
    ]

    notification_count, recent_notifications = get_notifications(leader_id, cur)

    cur.execute(
        """
        SELECT COUNT(*)
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s 
            AND t.status = 'approved'
            AND t.completed_at >= CURRENT_DATE - INTERVAL '14 days'
            AND t.completed_at < CURRENT_DATE - INTERVAL '7 days';
    """,
        (leader_id,),
    )
    last_week_completed = cur.fetchone()[0] or 0

    if last_week_completed > 0:
        completed_change = (
            (completed_tasks - last_week_completed) / last_week_completed
        ) * 100
        completed_change_str = f"{'+' if completed_change >= 0 else ''}{completed_change:.1f}% from last week"
    else:
        completed_change_str = "No data from last week"

    cur.execute(
        """
        SELECT COUNT(*)
        FROM project_members pm
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s 
            AND pm.joined_at >= CURRENT_DATE - INTERVAL '7 days'
            AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL);
    """,
        (leader_id,),
    )
    new_members = cur.fetchone()[0] or 0

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/dashboard.html",
        user_name=user_name,
        active_projects=active_projects,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        team_members=team_members,
        completed_change_str=completed_change_str,
        new_members=new_members,
        chart_labels=chart_labels,
        chart_values=chart_values,
        recent_activities=recent_activities,
        notification_count=notification_count,
        recent_notifications=recent_notifications,
        total_tasks=total_tasks,
    )


@project_leader_bp.route("/create_task", methods=["POST"])
def create_task():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    project = get_leader_project(leader_id, cur)
    if not project:
        cur.close()
        conn.close()
        return (
            jsonify({"success": False, "error": "No project found for this leader"}),
            404,
        )

    # Check if project is closed
    cur.execute("SELECT status FROM projects WHERE project_id = %s", (project[0],))
    status = cur.fetchone()[0]
    if status == "closed":
        cur.close()
        conn.close()
        return (
            jsonify(
                {"success": False, "error": "Project is closed. Cannot create tasks."}
            ),
            400,
        )

    cur.execute(
        """
        INSERT INTO tasks 
        (project_id, title, description, priority, assigned_to, assigned_by, due_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'in_progress')
    """,
        (
            project[0],
            request.form["title"],
            request.form.get("description", ""),
            request.form["priority"].lower(),
            int(request.form["assigned_to"]),
            leader_id,
            request.form["due_date"],
        ),
    )

    # 🔥 AUTO-RECALCULATE project progress based on approved tasks
    cur.execute(
        """
        UPDATE projects
        SET progress = (
            SELECT CASE
                WHEN COUNT(*) = 0 THEN 1
                ELSE GREATEST(1, ROUND(COUNT(*) FILTER (WHERE status = 'approved') * 100.0 / COUNT(*)))
            END
            FROM tasks WHERE project_id = %s
        ),
        updated_at = NOW()
        WHERE project_id = %s
        """,
        (project[0], project[0]),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Task created successfully"})


@project_leader_bp.route("/export_pdf")
def export_pdf():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    project = get_leader_project(leader_id, cur)
    if not project:
        cur.close()
        conn.close()
        return "No project found"

    project_id = project[0]

    cur.execute(
        """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'approved') as completed,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress,
            COUNT(*) FILTER (WHERE status = 'Pending Review') as pending_review,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'approved') as overdue
        FROM tasks WHERE project_id = %s
    """,
        (project_id,),
    )
    stats = cur.fetchone()

    cur.execute(
        """
        SELECT u.name, u.designation, COUNT(t.task_id) as tasks,
               COUNT(*) FILTER (WHERE t.status = 'approved') as completed,
               COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'approved') as overdue
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        GROUP BY u.user_id, u.name, u.designation
    """,
        (project_id,),
    )
    team_data = cur.fetchall()

    cur.execute(
        "SELECT status, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY status",
        (project_id,),
    )
    tasks_by_status = cur.fetchall()

    cur.execute(
        "SELECT priority, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY priority",
        (project_id,),
    )
    tasks_by_priority = cur.fetchall()

    cur.close()
    conn.close()

    total = stats[0] or 0
    completion_rate = round((stats[1] or 0) / total * 100, 1) if total > 0 else 0
    buffer = generate_pdf_report(
        project,
        stats,
        team_data,
        tasks_by_status,
        tasks_by_priority,
        completion_rate=completion_rate,
    )

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'attachment; filename=project_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    )
    return response


@project_leader_bp.route("/export_csv")
def export_csv():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT t.title, t.description, t.status, t.priority, u.name as assigned_to, t.due_date
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        JOIN users u ON t.assigned_to = u.user_id
        WHERE p.leader_id = %s
        ORDER BY t.created_at DESC
    """,
        (leader_id,),
    )
    tasks = cur.fetchall()
    cur.close()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(
        ["Title", "Description", "Status", "Priority", "Assigned To", "Due Date"]
    )
    for task in tasks:
        cw.writerow(task)

    output = si.getvalue()
    si.close()

    response = make_response(output)
    response.headers["Content-Disposition"] = (
        f'attachment; filename=tasks_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )
    response.headers["Content-type"] = "text/csv"
    return response


@project_leader_bp.route("/email_report", methods=["POST"])
def email_report():
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    leader_id = session["user_id"]

    recipients = [
        r.strip() for r in request.form.get("recipients", "").split(",") if r.strip()
    ]
    subject = request.form.get("subject", "Project Report")
    message = request.form.get("message", "")

    if not recipients:
        return jsonify({"error": "No recipients specified"}), 400

    conn = get_db()
    cur = conn.cursor()

    project = get_leader_project(leader_id, cur)
    if not project:
        cur.close()
        conn.close()
        return jsonify({"error": "No project found"}), 404

    project_id = project[0]

    cur.execute(
        """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'approved') as completed,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress,
            COUNT(*) FILTER (WHERE status = 'Pending Review') as pending_review,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'approved') as overdue
        FROM tasks WHERE project_id = %s
    """,
        (project_id,),
    )
    stats = cur.fetchone()

    cur.execute(
        """
        SELECT u.name, u.designation, COUNT(t.task_id) as tasks,
               COUNT(*) FILTER (WHERE t.status = 'approved') as completed,
               COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'approved') as overdue
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        GROUP BY u.user_id, u.name, u.designation
    """,
        (project_id,),
    )
    team_data = cur.fetchall()

    cur.execute(
        "SELECT status, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY status",
        (project_id,),
    )
    tasks_by_status = cur.fetchall()

    cur.execute(
        "SELECT priority, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY priority",
        (project_id,),
    )
    tasks_by_priority = cur.fetchall()

    cur.execute(
        """
        (SELECT 'task_completed' as type, t.title, u.name, t.completed_at
        FROM tasks t JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC LIMIT 5)
        UNION ALL
        (SELECT 'member_joined' as type, pm.role_in_project, u.name, pm.joined_at
        FROM project_members pm JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = %s AND (pm.is_deleted = FALSE OR pm.is_deleted IS NULL)
        ORDER BY pm.joined_at DESC LIMIT 5)
        ORDER BY completed_at DESC LIMIT 10;
    """,
        (project_id, project_id),
    )
    recent_activities = cur.fetchall()

    cur.execute(
        """
        SELECT COUNT(*) FROM project_members 
        WHERE project_id = %s AND (is_deleted = FALSE OR is_deleted IS NULL)
    """,
        (project_id,),
    )
    team_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    total = stats[0] or 0
    completed = stats[1] or 0
    completion_rate = round((completed / total * 100), 1) if total > 0 else 0

    buffer = generate_pdf_report(
        project,
        stats,
        team_data,
        tasks_by_status,
        tasks_by_priority,
        recent_activities,
        completion_rate,
    )

    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=message
            or f"Please find attached the project report for {project[1]}.\n\nTeam Size: {team_count}\nTotal Tasks: {total}\nCompleted: {completed}\nCompletion Rate: {completion_rate}%",
            sender=current_app.config.get(
                "MAIL_DEFAULT_SENDER", "noreply@collabhub.com"
            ),
        )
        msg.attach(
            f"project_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            "application/pdf",
            buffer.getvalue(),
        )
        from app import mail

        mail.send(msg)
        return jsonify({"success": True, "message": "Report sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@project_leader_bp.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT t.task_id 
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """,
        (task_id, leader_id),
    )
    if not cur.fetchone():
        cur.close()
        conn.close()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Task not found or you don't have permission to delete it",
                }
            ),
            403,
        )
    cur.execute(
        """
        SELECT p.status
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s
    """,
        (task_id,),
    )
    status = cur.fetchone()[0]
    if status == "closed":
        cur.close()
        conn.close()
        return (
            jsonify(
                {"success": False, "error": "Project is closed. Cannot delete tasks."}
            ),
            400,
        )
    cur.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Task deleted successfully"})


@project_leader_bp.route("/get_task/<int:task_id>", methods=["GET"])
def get_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT t.task_id, t.title, t.description, t.assigned_to,
               t.project_id, t.priority, t.status, t.due_date
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """,
        (task_id, leader_id),
    )

    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(
        {
            "task_id": task[0],
            "title": task[1],
            "description": task[2],
            "assigned_to": task[3],
            "project_id": task[4],
            "priority": task[5],
            "status": task[6],
            "due_date": task[7].strftime("%Y-%m-%d") if task[7] else None,
        }
    )


@project_leader_bp.route("/update_task/<int:task_id>", methods=["POST"])
def update_task(task_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    # Verify task belongs to leader
    cur.execute(
        """
        SELECT t.task_id 
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """,
        (task_id, leader_id),
    )
    if not cur.fetchone():
        cur.close()
        conn.close()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Task not found or you don't have permission to update it",
                }
            ),
            403,
        )

    # Check if the project is closed
    cur.execute(
        """
        SELECT p.status
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s
    """,
        (task_id,),
    )
    status = cur.fetchone()[0]
    if status == "closed":
        cur.close()
        conn.close()
        return (
            jsonify(
                {"success": False, "error": "Project is closed. Cannot update tasks."}
            ),
            400,
        )

    cur.execute(
        """
        UPDATE tasks 
        SET title = %s, description = %s, assigned_to = %s, project_id = %s,
            priority = %s, due_date = %s, updated_at = CURRENT_TIMESTAMP
        WHERE task_id = %s
        """,
        (
            request.form["title"],
            request.form.get("description", ""),
            int(request.form["assigned_to"]),
            int(request.form["project_id"]),
            request.form["priority"].lower(),
            request.form.get("due_date"),
            task_id,
        ),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Task updated successfully"})


@project_leader_bp.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE users 
            SET name = %s, email = %s, designation = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id;
        """,
            (
                request.form.get("name"),
                request.form.get("email"),
                request.form.get("designation"),
                leader_id,
            ),
        )

        if not cur.fetchone():
            conn.rollback()
            return jsonify({"success": False, "error": "User not found"}), 404

        conn.commit()
        return jsonify({"success": True, "message": "Profile updated successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@project_leader_bp.route("/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    leader_id = session["user_id"]
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return jsonify({"success": False, "error": "All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"success": False, "error": "New passwords do not match"}), 400

    if len(new_password) < 6:
        return (
            jsonify(
                {"success": False, "error": "Password must be at least 6 characters"}
            ),
            400,
        )

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT password_hash FROM auth WHERE user_id = %s;", (leader_id,))
        auth_data = cur.fetchone()

        if not auth_data:
            return (
                jsonify({"success": False, "error": "User authentication not found"}),
                404,
            )

        if auth_data[0] != current_password:  # NOTE: Use proper hash verification here!
            return (
                jsonify({"success": False, "error": "Current password is incorrect"}),
                400,
            )

        cur.execute(
            """
            UPDATE auth 
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """,
            (new_password, leader_id),
        )  # NOTE: Hash the password before storing!

        conn.commit()
        return jsonify({"success": True, "message": "Password changed successfully!"})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@project_leader_bp.route("/remove_team_member", methods=["POST"])
def remove_team_member():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    user_id = request.form["user_id"]

    conn = get_db()
    cur = conn.cursor()

    project = get_leader_project(leader_id, cur)
    if not project:
        cur.close()
        conn.close()
        return jsonify({"success": False, "error": "Project not found"}), 404

    # Check if project is closed
    cur.execute("SELECT status FROM projects WHERE project_id = %s", (project[0],))
    status = cur.fetchone()[0]
    if status == "closed":
        cur.close()
        conn.close()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Project is closed. Cannot remove team members.",
                }
            ),
            400,
        )

    cur.execute(
        """
        UPDATE project_members
        SET is_deleted = TRUE
        WHERE project_id = %s AND user_id = %s
    """,
        (project[0], user_id),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "message": "Team member removed successfully"})


@project_leader_bp.route("/approve_task/<int:task_id>", methods=["POST"])
def approve_task(task_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT t.task_id, t.title, u.name
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            JOIN users u ON t.assigned_to = u.user_id
            WHERE t.task_id = %s AND p.leader_id = %s AND t.status = 'submitted'
        """,
            (task_id, leader_id),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return (
                jsonify({"success": False, "error": "Task not found or not submitted"}),
                404,
            )

        # Check if project is closed
        cur.execute(
            """
            SELECT p.status
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            WHERE t.task_id = %s
        """,
            (task_id,),
        )
        status = cur.fetchone()[0]
        if status == "closed":
            cur.close()
            conn.close()
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Project is closed. Cannot approve tasks.",
                    }
                ),
                400,
            )

        cur.execute(
            """
            UPDATE tasks 
            SET status = 'approved',
                approved_at = CURRENT_TIMESTAMP,
                approved_by = %s,
                last_action_by = %s,
                last_action_at = CURRENT_TIMESTAMP,
                rejected_at = NULL,
                rejection_reason = NULL
            WHERE task_id = %s
        """,
            (leader_id, leader_id, task_id),
        )

        # 🔥 AUTO-RECALCULATE project progress based on approved tasks
        cur.execute(
            """
            UPDATE projects
            SET progress = (
                SELECT CASE
                    WHEN COUNT(*) = 0 THEN 1
                    ELSE GREATEST(1, ROUND(COUNT(*) FILTER (WHERE status = 'approved') * 100.0 / COUNT(*)))
                END
                FROM tasks WHERE project_id = projects.project_id
            ),
            updated_at = NOW()
            WHERE project_id = (SELECT project_id FROM tasks WHERE task_id = %s)
            """,
            (task_id,),
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"success": True, "message": "Task approved successfully"})

    except Exception as e:
        print("Error in approve_task:", str(e))
        return jsonify({"success": False, "error": "Server error occurred"}), 500


# ============================
# REJECT TASK
# ============================
@project_leader_bp.route("/reject_task/<int:task_id>", methods=["POST"])
def reject_task(task_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid request"}), 400

    reason = data.get("reason", "").strip()
    if not reason:
        return jsonify({"success": False, "error": "Rejection reason required"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT t.task_id, t.title, u.name
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            JOIN users u ON t.assigned_to = u.user_id
            WHERE t.task_id = %s AND p.leader_id = %s AND t.status = 'submitted'
        """,
            (task_id, leader_id),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return (
                jsonify({"success": False, "error": "Task not found or not submitted"}),
                404,
            )

        # Check if project is closed
        cur.execute(
            """
            SELECT p.status
            FROM tasks t
            JOIN projects p ON t.project_id = p.project_id
            WHERE t.task_id = %s
        """,
            (task_id,),
        )
        status = cur.fetchone()[0]
        if status == "closed":
            cur.close()
            conn.close()
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Project is closed. Cannot reject tasks.",
                    }
                ),
                400,
            )

        cur.execute(
            """
            UPDATE tasks 
            SET status = 'in_progress',
                rejected_at = CURRENT_TIMESTAMP,
                rejection_reason = %s,
                last_action_by = %s,
                last_action_at = CURRENT_TIMESTAMP,
                approved_at = NULL,
                approved_by = NULL
            WHERE task_id = %s
        """,
            (reason, leader_id, task_id),
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(
            {"success": True, "message": "Task rejected and sent back for revision"}
        )

    except Exception as e:
        print("Error in reject_task:", str(e))
        return jsonify({"success": False, "error": "Server error occurred"}), 500


# ============================
# SUBMIT PROJECT (Leader marks project as complete)
# ============================


@project_leader_bp.route("/submit_project/<int:project_id>", methods=["POST"])
def submit_project(project_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Login required"}), 401

    leader_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    try:
        # Make sure this project actually belongs to this leader
        cur.execute(
            """
            SELECT project_id, project_name
            FROM projects
            WHERE project_id = %s AND leader_id = %s AND status = 'ongoing'
            """,
            (project_id, leader_id),
        )
        project = cur.fetchone()

        if not project:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Project not found or not in ongoing status",
                    }
                ),
                404,
            )

        # Update project status to 'completed' — awaiting admin review
        cur.execute(
            """
            UPDATE projects
            SET status = 'completed', updated_at = NOW()
            WHERE project_id = %s
            """,
            (project_id,),
        )

        # Find admin user_id to send notification
        cur.execute("SELECT user_id FROM users WHERE role = 'admin' LIMIT 1")
        admin = cur.fetchone()

        if admin:
            admin_id = admin[0]
            cur.execute(
                """
                INSERT INTO notifications (sender_id, receiver_id, title, message, type, is_read, sent_at)
                VALUES (%s, %s, %s, %s, %s, false, NOW())
                """,
                (
                    leader_id,
                    admin_id,
                    "Project Submitted for Review",
                    f"Project '{project[1]}' has been marked as complete by the leader and is awaiting your review.",
                    "project_review",
                ),
            )

        conn.commit()
        return jsonify(
            {"success": True, "message": "Project submitted for review successfully!"}
        )

    except Exception as e:
        conn.rollback()
        print("Error in submit_project:", str(e))
        return jsonify({"success": False, "error": "Something went wrong"}), 500

    finally:
        cur.close()
        conn.close()
