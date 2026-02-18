from flask import Blueprint, render_template, session, jsonify,request,redirect,url_for
from database.db import get_db
from datetime import datetime

from flask import make_response, jsonify
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from flask_mail import Mail, Message


project_leader_bp = Blueprint("project_leader", __name__)

@project_leader_bp.route("/my_team")
def my_team_page():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    # Get team members (users in leader's projects)
    cur.execute("""
        SELECT u.user_id,u.name,u.email,u.designation,p.project_name,pm.role_in_project
        FROM users u
        JOIN project_members pm 
            ON u.user_id = pm.user_id
        JOIN projects p 
            ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        ORDER BY u.name;
    """, (leader_id,))
    team = cur.fetchall()
    
    # Get leader's projects for dropdown
    cur.execute("""
        SELECT project_id, project_name 
        FROM projects 
        WHERE leader_id = %s;
    """, (leader_id,))
    leader_projects = cur.fetchall()
    
    # Get available employees - users who are NOT in ANY project
    # AND are employees (not leaders/admins)
    cur.execute("""
        SELECT u.user_id, u.name, u.designation
        FROM users u
        LEFT JOIN project_members pm ON u.user_id = pm.user_id
        WHERE u.role = 'employee' 
        AND u.user_id != %s
        AND pm.user_id IS NULL
        ORDER BY u.name;
    """, (leader_id,))
    available_employees = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/my_team.html",
        team=team,
        leader_projects=leader_projects,
        available_employees=available_employees
    )


@project_leader_bp.route("/myproject")
def my_project():
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get the ONE project this leader manages
    cur.execute("""
        SELECT 
            project_id,
            project_name,
            features as description,
            status,
            start_date,
            end_date
        FROM projects 
        WHERE leader_id = %s
        LIMIT 1;
    """, (leader_id,))
    
    project_row = cur.fetchone()
    
    if not project_row:
        return render_template("projectLeader/projectDetails.html", 
                             project=None, tasks=[], employees=[], task_stats={})
    
    # Unpack project data
    project = {
        'project_id': project_row[0],
        'project_name': project_row[1],
        'features': project_row[2],
        'status': project_row[3],
        'start_date': project_row[4],
        'end_date': project_row[5]
    }
    
    project_id = project['project_id']
    
    # Get tasks for THIS project only
    cur.execute("""
        SELECT 
            t.task_id,
            t.title,
            t.description,
            t.status,
            t.priority,
            t.due_date,
            u.name as assigned_to_name
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
    """, (project_id,))
    
    task_rows = cur.fetchall()
    tasks = []
    for row in task_rows:
        tasks.append({
            'task_id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'priority': row[4],
            'due_date': row[5],
            'assigned_to_name': row[6]
        })
    
    # Get employees assigned to THIS project (from project_members)
    cur.execute("""
        SELECT 
            u.user_id,
            u.name,
            u.email,
            pm.role_in_project
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        WHERE pm.project_id = %s
        ORDER BY u.name;
    """, (project_id,))
    
    emp_rows = cur.fetchall()
    employees = []
    for row in emp_rows:
        employees.append({
            'user_id': row[0],
            'name': row[1],
            'email': row[2],
            'role_in_project': row[3]
        })
    
    # Calculate task statistics for this project
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t['status'] and t['status'].lower() == 'completed')
    pending_tasks = total_tasks - completed_tasks
    progress = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    task_stats = {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'progress': progress
    }
    
    cur.close()
    conn.close()
    
    return render_template(
        "projectLeader/projectDetails.html",
        project=project,
        tasks=tasks,
        employees=employees,
        task_stats=task_stats,
        now=datetime.now().date()  # <-- CHANGED THIS
    )

@project_leader_bp.route("/tasks")
def tasks():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()

    # Get tasks
    cur.execute("""
    SELECT 
        t.task_id,
        t.title,
        t.description,
        t.priority,
        t.status,
        t.due_date,
        p.project_name,
        u.name AS assigned_to_name
    FROM tasks t
    JOIN projects p ON t.project_id = p.project_id
    JOIN users u ON t.assigned_to = u.user_id
    WHERE p.leader_id = %s
    ORDER BY t.created_at DESC;
    """, (leader_id,))
    tasks = cur.fetchall()

    # Get task summary for leader's tasks only
    cur.execute("""
    SELECT 
        COUNT(*) FILTER (WHERE t.status = 'Completed'),
        COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'Completed'),
        COUNT(*) FILTER (WHERE t.status = 'In Progress'),
        COUNT(*) FILTER (WHERE t.status = 'Pending Review')
    FROM tasks t
    JOIN projects p ON t.project_id = p.project_id
    WHERE p.leader_id = %s;
    """, (leader_id,))
    task_summary = cur.fetchone()

    # Get leader's projects
    cur.execute("""
        SELECT project_id, project_name 
        FROM projects 
        WHERE leader_id = %s;
    """, (leader_id,))
    projects = cur.fetchall()

    # Get ONLY team members from leader's projects
    cur.execute("""
        SELECT DISTINCT u.user_id, u.name
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        ORDER BY u.name;
    """, (leader_id,))
    users = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "projectLeader/tasks.html",
        tasks=tasks,
        projects=projects,
        users=users,
        task_summary=task_summary,
        now=datetime.now().date() 
    )

@project_leader_bp.route("/add_team_member", methods=["POST"])
def add_team_member():
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    user_id = request.form["user_id"]
    role = request.form["role"]
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get the leader's project (assuming they have only one)
    cur.execute("""
        SELECT project_id FROM projects 
        WHERE leader_id = %s
        LIMIT 1;
    """, (leader_id,))
    
    project_row = cur.fetchone()
    if not project_row:
        cur.close()
        conn.close()
        return "No project found for this leader"
    
    project_id = project_row[0]
    
    # Add member to project
    cur.execute("""
        INSERT INTO project_members (project_id, user_id, role_in_project, joined_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (project_id, user_id) DO NOTHING;
    """, (project_id, user_id, role))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for("project_leader.my_team_page"))


@project_leader_bp.route("/reports")
def reports():
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    
    # Get leader's project
    cur.execute("""
        SELECT project_id, project_name, start_date, end_date, status, progress
        FROM projects 
        WHERE leader_id = %s
        LIMIT 1;
    """, (leader_id,))
    project = cur.fetchone()
    
    if not project:
        return render_template("projectLeader/reports.html", error="No project found")
    
    project_id = project[0]
    
    # Overview stats
    cur.execute("""
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'Completed') as completed_tasks,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress_tasks,
            COUNT(*) FILTER (WHERE status = 'Pending Review') as pending_review_tasks,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'Completed') as overdue_tasks
        FROM tasks 
        WHERE project_id = %s;
    """, (project_id,))
    task_stats = cur.fetchone()
    
    # Team members count
    cur.execute("""
        SELECT COUNT(*) 
        FROM project_members 
        WHERE project_id = %s;
    """, (project_id,))
    team_count = cur.fetchone()[0]
    
    # Completion rate
    total_tasks = task_stats[0] or 0
    completed_tasks = task_stats[1] or 0
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    # Team performance
    cur.execute("""
        SELECT 
            u.user_id,
            u.name,
            u.designation,
            COUNT(t.task_id) as total_assigned,
            COUNT(*) FILTER (WHERE t.status = 'Completed') as tasks_completed,
            COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'Completed') as overdue_tasks
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        GROUP BY u.user_id, u.name, u.designation
        ORDER BY tasks_completed DESC;
    """, (project_id,))
    team_performance = cur.fetchall()
    
    # Tasks by status for pie chart
    cur.execute("""
        SELECT status, COUNT(*) 
        FROM tasks 
        WHERE project_id = %s 
        GROUP BY status;
    """, (project_id,))
    tasks_by_status = cur.fetchall()
    
    # Tasks by priority
    cur.execute("""
        SELECT priority, COUNT(*) 
        FROM tasks 
        WHERE project_id = %s 
        GROUP BY priority;
    """, (project_id,))
    tasks_by_priority = cur.fetchall()
    
    # Weekly task completion (last 4 weeks)
    cur.execute("""
        SELECT 
            DATE_TRUNC('week', completed_at) as week,
            COUNT(*) as tasks_completed
        FROM tasks 
        WHERE project_id = %s 
            AND completed_at IS NOT NULL
            AND completed_at >= CURRENT_DATE - INTERVAL '4 weeks'
        GROUP BY week
        ORDER BY week;
    """, (project_id,))
    weekly_completion = cur.fetchall()
    
    # Recent activities
    cur.execute("""
        (SELECT 
            'task_completed' as type,
            t.title as description,
            u.name as user_name,
            t.completed_at as created_at
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC
        LIMIT 5)
        UNION ALL
        (SELECT 
            'member_joined' as type,
            pm.role_in_project as description,
            u.name as user_name,
            pm.joined_at as created_at
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = %s
        ORDER BY pm.joined_at DESC
        LIMIT 5)
        ORDER BY created_at DESC
        LIMIT 10;
    """, (project_id, project_id))
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
        weekly_completion=weekly_completion,
        recent_activities=recent_activities
    )

@project_leader_bp.route("/my_profile")
def my_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    leader_id = session["user_id"]
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get user profile data
    cur.execute("""
        SELECT 
            user_id,
            name,
            email,
            role,
            designation,
            avatar,
            created_at as joining_date
        FROM users 
        WHERE user_id = %s;
    """, (leader_id,))
    
    user_data = cur.fetchone()
    
    if not user_data:
        cur.close()
        conn.close()
        return "User not found", 404
    
    # Get projects led by this leader
    cur.execute("""
        SELECT 
            project_id,
            project_name,
            status,
            progress,
            start_date,
            end_date
        FROM projects 
        WHERE leader_id = %s
        ORDER BY 
            CASE 
                WHEN status != 'completed' THEN 1 
                ELSE 2 
            END,
            created_at DESC;
    """, (leader_id,))
    
    projects = cur.fetchall()
    
    # Get team stats
    cur.execute("""
        SELECT 
            COUNT(DISTINCT pm.user_id) as team_size,
            COUNT(DISTINCT t.task_id) as total_tasks,
            COUNT(DISTINCT CASE WHEN t.status = 'Completed' THEN t.task_id END) as completed_tasks
        FROM projects p
        LEFT JOIN project_members pm ON p.project_id = pm.project_id
        LEFT JOIN tasks t ON p.project_id = t.project_id
        WHERE p.leader_id = %s;
    """, (leader_id,))
    
    team_stats = cur.fetchone()
    
    # ===== ADD THIS: Get notifications count =====
    cur.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE receiver_id = %s AND is_read = false;
    """, (leader_id,))
    notification_count = cur.fetchone()[0] or 0
    
    # Get recent notifications
    cur.execute("""
        SELECT 
            n.message,
            n.sent_at,
            u.name as sender_name
        FROM notifications n
        JOIN users u ON n.sender_id = u.user_id
        WHERE n.receiver_id = %s AND n.is_read = false
        ORDER BY n.sent_at DESC
        LIMIT 3;
    """, (leader_id,))
    
    notifications = cur.fetchall()
    recent_notifications = []
    for notif in notifications:
        recent_notifications.append({
            'message': notif[0],
            'sent_at': notif[1].strftime('%b %d, %Y') if notif[1] else 'Recently',
            'sender_name': notif[2]
        })
    # ==============================================
    
    cur.close()
    conn.close()
    
    # Format user data
    user = {
        'user_id': user_data[0],
        'name': user_data[1],
        'email': user_data[2],
        'role': user_data[3],
        'designation': user_data[4] or 'Project Leader',
        'avatar': user_data[5],
        'joining_date': user_data[6].strftime('%b %d, %Y') if user_data[6] else 'N/A',
        'phone': 'Not provided',
        'bio': 'No bio available.',
        'profile_completion': 70
    }
    
    # Format projects
    project_list = []
    for p in projects:
        project_list.append({
            'id': p[0],
            'name': p[1],
            'status': p[2] or 'active',
            'progress': p[3] or 0,
            'start_date': p[4].strftime('%b %d, %Y') if p[4] else 'N/A',
            'end_date': p[5].strftime('%b %d, %Y') if p[5] else 'N/A'
        })
    
    # Format team stats
    stats = {
        'team_size': team_stats[0] or 0,
        'total_tasks': team_stats[1] or 0,
        'completed_tasks': team_stats[2] or 0,
        'completion_rate': round((team_stats[2] or 0) / (team_stats[1] or 1) * 100, 1)
    }
    
    return render_template(
        "projectLeader/my_profile.html",
        user=user,
        projects=project_list,
        stats=stats,
        notification_count=notification_count,  # ADD THIS
        recent_notifications=recent_notifications  # ADD THIS
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
    
    # Get the logged-in user's name
    cur.execute("""
        SELECT name FROM users WHERE user_id = %s;
    """, (leader_id,))
    user_result = cur.fetchone()
    user_name = user_result[0] if user_result else "User"
    
    # Get active projects count
    cur.execute("""
        SELECT COUNT(*) 
        FROM projects 
        WHERE leader_id = %s AND status != 'completed';
    """, (leader_id,))
    active_projects = cur.fetchone()[0] or 0
    
    # Get tasks statistics
    cur.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE t.status = 'Completed') as completed_tasks,
            COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'Completed') as overdue_tasks,
            COUNT(*) as total_tasks
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s;
    """, (leader_id,))
    task_stats = cur.fetchone()
    completed_tasks = task_stats[0] or 0
    overdue_tasks = task_stats[1] or 0
    total_tasks = task_stats[2] or 0
    
    # Get team members count
    cur.execute("""
        SELECT COUNT(DISTINCT u.user_id)
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s;
    """, (leader_id,))
    team_members = cur.fetchone()[0] or 0
    
    # Get weekly task completion data for chart (last 7 days)
    cur.execute("""
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
    """, (leader_id,))
    weekly_data = cur.fetchall()
    
    # Prepare chart data (fill in missing days)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    chart_labels = []
    chart_values = []
    
    # Get current date and calculate last 7 days
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_name = day.strftime('%a')
        chart_labels.append(day_name)
        
        # Find if we have data for this day
        day_data = 0
        for data in weekly_data:
            if data[0] == day_name:
                day_data = data[1]
                break
        chart_values.append(day_data)
    
    # Get recent activities
    cur.execute("""
        (SELECT 
            'task_completed' as type,
            t.title as description,
            u.name as user_name,
            t.completed_at as created_at,
            p.project_name
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC
        LIMIT 4)
        UNION ALL
        (SELECT 
            'member_joined' as type,
            pm.role_in_project as description,
            u.name as user_name,
            pm.joined_at as created_at,
            p.project_name
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s
        ORDER BY pm.joined_at DESC
        LIMIT 4)
        ORDER BY created_at DESC
        LIMIT 8;
    """, (leader_id, leader_id))
    activities = cur.fetchall()
    
    # Format activities for display
    recent_activities = []
    for act in activities:
        activity = {
            'type': act[0],
            'description': act[1],
            'user_name': act[2],
            'created_at': act[3],
            'project_name': act[4]
        }
        recent_activities.append(activity)
    
    # Get notifications count
    cur.execute("""
        SELECT COUNT(*) 
        FROM notifications 
        WHERE receiver_id = %s AND is_read = false;
    """, (leader_id,))
    notification_count = cur.fetchone()[0] or 0
    
    # Get sample notifications (last 3 unread)
    cur.execute("""
        SELECT 
            n.title,
            n.message,
            n.sent_at,
            u.name as sender_name
        FROM notifications n
        JOIN users u ON n.sender_id = u.user_id
        WHERE n.receiver_id = %s AND n.is_read = false
        ORDER BY n.sent_at DESC
        LIMIT 3;
    """, (leader_id,))
    notifications = cur.fetchall()
    
    # Format notifications
    recent_notifications = []
    for notif in notifications:
        notification = {
            'title': notif[0],
            'message': notif[1],
            'sent_at': notif[2],
            'sender_name': notif[3]
        }
        recent_notifications.append(notification)
    
    # Calculate percentage changes
    # Get last week's completed tasks for comparison
    cur.execute("""
        SELECT COUNT(*)
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE p.leader_id = %s 
            AND t.status = 'Completed'
            AND t.completed_at >= CURRENT_DATE - INTERVAL '14 days'
            AND t.completed_at < CURRENT_DATE - INTERVAL '7 days';
    """, (leader_id,))
    last_week_completed = cur.fetchone()[0] or 0
    
    # Calculate change percentage
    if last_week_completed > 0:
        completed_change = ((completed_tasks - last_week_completed) / last_week_completed) * 100
        completed_change_str = f"{'+' if completed_change >= 0 else ''}{completed_change:.1f}% from last week"
    else:
        completed_change_str = "No data from last week"
    
    # Get new members this week
    cur.execute("""
        SELECT COUNT(*)
        FROM project_members pm
        JOIN projects p ON pm.project_id = p.project_id
        WHERE p.leader_id = %s 
            AND pm.joined_at >= CURRENT_DATE - INTERVAL '7 days';
    """, (leader_id,))
    new_members = cur.fetchone()[0] or 0
    
    cur.close()
    conn.close()
    
    return render_template(
        "projectLeader/dashboard.html",
        user_name=user_name,  # Add this line to pass the user's name
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
        total_tasks=total_tasks
    )

@project_leader_bp.route("/create_task", methods=["POST"])
def create_task():
    if "user_id" not in session:
        return "Login required"

    leader_id = session["user_id"]

    title = request.form["title"]
    description = request.form.get("description", "")
    assigned_to = int(request.form["assigned_to"])
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    conn = get_db()
    cur = conn.cursor()
    
    # Get leader's project
    cur.execute("""
        SELECT project_id FROM projects 
        WHERE leader_id = %s
        LIMIT 1;
    """, (leader_id,))
    
    project_row = cur.fetchone()
    if not project_row:
        cur.close()
        conn.close()
        return "No project found for this leader"
    
    project_id = project_row[0]

    cur.execute("""
        INSERT INTO tasks 
        (project_id, title, description, priority, assigned_to, assigned_by, due_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'In Progress')
    """, (project_id, title, description, priority, assigned_to, leader_id, due_date))

    conn.commit()
    cur.close()
    conn.close()

    return redirect("/projectleader/tasks")

@project_leader_bp.route("/export_pdf")
def export_pdf():
    """Generate and download PDF report"""
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    
    # Get all the same data as reports page
    conn = get_db()
    cur = conn.cursor()
    
    # Get project data
    cur.execute("SELECT project_id, project_name FROM projects WHERE leader_id = %s LIMIT 1", (leader_id,))
    project = cur.fetchone()
    
    if not project:
        return "No project found"
    
    project_id = project[0]
    
    # Get all report data (similar to reports route)
    cur.execute("""
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'Completed') as completed,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'Completed') as overdue
        FROM tasks WHERE project_id = %s
    """, (project_id,))
    stats = cur.fetchone()
    
    cur.execute("""
        SELECT u.name, u.designation, COUNT(t.task_id) as tasks,
               COUNT(*) FILTER (WHERE t.status = 'Completed') as completed
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        GROUP BY u.user_id, u.name, u.designation
    """, (project_id,))
    team_data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Generate PDF using reportlab
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2563eb')
    )
    story.append(Paragraph(f"Project Report: {project[1]}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Add stats
    story.append(Paragraph("Task Statistics", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    stats_data = [
        ['Metric', 'Count'],
        ['Total Tasks', str(stats[0] or 0)],
        ['Completed', str(stats[1] or 0)],
        ['In Progress', str(stats[2] or 0)],
        ['Overdue', str(stats[3] or 0)]
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 30))
    
    # Add team data
    story.append(Paragraph("Team Performance", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    team_table_data = [['Name', 'Role', 'Tasks', 'Completed']]
    for member in team_data:
        team_table_data.append([member[0], member[1] or 'N/A', str(member[2] or 0), str(member[3] or 0)])
    
    team_table = Table(team_table_data)
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(team_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Return PDF as download
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=project_report_{datetime.now().strftime("%Y%m%d")}.pdf'
    
    return response


@project_leader_bp.route("/export_csv")
def export_csv():
    """Export task data as CSV"""
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            t.title,
            t.description,
            t.status,
            t.priority,
            u.name as assigned_to,
            t.due_date
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        JOIN users u ON t.assigned_to = u.user_id
        WHERE p.leader_id = %s
        ORDER BY t.created_at DESC
    """, (leader_id,))
    
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    # Create CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Title', 'Description', 'Status', 'Priority', 'Assigned To', 'Due Date'])
    
    for task in tasks:
        cw.writerow(task)
    
    output = si.getvalue()
    si.close()
    
    response = make_response(output)
    response.headers['Content-Disposition'] = f'attachment; filename=tasks_export_{datetime.now().strftime("%Y%m%d")}.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response


@project_leader_bp.route("/email_report", methods=["POST"])
def email_report():
    """Generate PDF and send via email"""
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    
    leader_id = session["user_id"]
    
    # Get form data
    recipients = request.form.get("recipients", "").split(",")
    recipients = [r.strip() for r in recipients if r.strip()]
    subject = request.form.get("subject", "Project Report")
    message = request.form.get("message", "")
    
    if not recipients:
        return jsonify({"error": "No recipients specified"}), 400
    
    # Get project data for PDF
    conn = get_db()
    cur = conn.cursor()
    
    # Get leader's project
    cur.execute("SELECT project_id, project_name FROM projects WHERE leader_id = %s LIMIT 1", (leader_id,))
    project = cur.fetchone()
    
    if not project:
        return jsonify({"error": "No project found"}), 404
    
    project_id = project[0]
    
    # Get task stats
    cur.execute("""
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(*) FILTER (WHERE status = 'Completed') as completed,
            COUNT(*) FILTER (WHERE status = 'In Progress') as in_progress,
            COUNT(*) FILTER (WHERE status = 'Pending Review') as pending_review,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'Completed') as overdue
        FROM tasks WHERE project_id = %s
    """, (project_id,))
    stats = cur.fetchone()
    
    # Get team performance
    cur.execute("""
        SELECT u.name, u.designation, COUNT(t.task_id) as tasks,
               COUNT(*) FILTER (WHERE t.status = 'Completed') as completed,
               COUNT(*) FILTER (WHERE t.due_date < CURRENT_DATE AND t.status != 'Completed') as overdue
        FROM users u
        JOIN project_members pm ON u.user_id = pm.user_id
        LEFT JOIN tasks t ON u.user_id = t.assigned_to AND t.project_id = pm.project_id
        WHERE pm.project_id = %s
        GROUP BY u.user_id, u.name, u.designation
    """, (project_id,))
    team_data = cur.fetchall()
    
    # Get tasks by status
    cur.execute("SELECT status, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY status", (project_id,))
    tasks_by_status = cur.fetchall()
    
    # Get tasks by priority
    cur.execute("SELECT priority, COUNT(*) FROM tasks WHERE project_id = %s GROUP BY priority", (project_id,))
    tasks_by_priority = cur.fetchall()
    
    # Get recent activities
    cur.execute("""
        (SELECT 
            'task_completed' as type,
            t.title as description,
            u.name as user_name,
            t.completed_at as created_at
        FROM tasks t
        JOIN users u ON t.assigned_to = u.user_id
        WHERE t.project_id = %s AND t.completed_at IS NOT NULL
        ORDER BY t.completed_at DESC
        LIMIT 5)
        UNION ALL
        (SELECT 
            'member_joined' as type,
            pm.role_in_project as description,
            u.name as user_name,
            pm.joined_at as created_at
        FROM project_members pm
        JOIN users u ON pm.user_id = u.user_id
        WHERE pm.project_id = %s
        ORDER BY pm.joined_at DESC
        LIMIT 5)
        ORDER BY created_at DESC
        LIMIT 10;
    """, (project_id, project_id))
    recent_activities = cur.fetchall()
    
    # Get team count
    cur.execute("SELECT COUNT(*) FROM project_members WHERE project_id = %s", (project_id,))
    team_count = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    # Calculate completion rate
    total_tasks = stats[0] or 0
    completed_tasks = stats[1] or 0
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    # Generate PDF using reportlab
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2563eb')
    )
    story.append(Paragraph(f"Project Report: {project[1]}", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Task Statistics
    story.append(Paragraph("Task Statistics", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    stats_data = [
        ['Metric', 'Count'],
        ['Total Tasks', str(stats[0] or 0)],
        ['Completed', str(stats[1] or 0)],
        ['In Progress', str(stats[2] or 0)],
        ['Pending Review', str(stats[3] or 0)],
        ['Overdue', str(stats[4] or 0)],
        ['Completion Rate', f"{completion_rate}%"]
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 30))
    
    # Tasks by Status
    story.append(Paragraph("Tasks by Status", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    status_data = [['Status', 'Count']]
    for status in tasks_by_status:
        status_data.append([status[0], str(status[1])])
    
    status_table = Table(status_data)
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(status_table)
    story.append(Spacer(1, 30))
    
    # Tasks by Priority
    story.append(Paragraph("Tasks by Priority", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    priority_data = [['Priority', 'Count']]
    for priority in tasks_by_priority:
        priority_data.append([priority[0], str(priority[1])])
    
    priority_table = Table(priority_data)
    priority_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(priority_table)
    story.append(Spacer(1, 30))
    
    # Team Performance
    story.append(Paragraph("Team Performance", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    team_table_data = [['Name', 'Role', 'Tasks', 'Completed', 'Overdue']]
    for member in team_data:
        team_table_data.append([
            member[0], 
            member[1] or 'N/A', 
            str(member[2] or 0), 
            str(member[3] or 0),
            str(member[4] or 0)
        ])
    
    team_table = Table(team_table_data)
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(team_table)
    story.append(Spacer(1, 30))
    
    # Recent Activities
    if recent_activities:
        story.append(Paragraph("Recent Activities", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        activities_data = [['User', 'Activity', 'Date']]
        for activity in recent_activities:
            if activity[0] == 'task_completed':
                desc = f"Completed task: {activity[1]}"
            else:
                desc = f"Joined as {activity[1]}"
            activities_data.append([
                activity[2],
                desc,
                activity[3].strftime('%b %d, %Y') if activity[3] else 'N/A'
            ])
        
        activities_table = Table(activities_data)
        activities_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6b7280')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(activities_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Send email
    try:
        from flask_mail import Message
        from flask import current_app
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=message or f"Please find attached the project report for {project[1]}.\n\nTeam Size: {team_count}\nTotal Tasks: {stats[0] or 0}\nCompleted: {stats[1] or 0}\nCompletion Rate: {completion_rate}%",
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@collabhub.com')
        )
        
        # Attach PDF
        msg.attach(
            f"project_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            "application/pdf",
            buffer.getvalue()
        )
        
        # Get mail instance from app
        from app import mail
        mail.send(msg)
        
        return jsonify({"success": True, "message": "Report sent successfully!"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@project_leader_bp.route("/delete_task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    
    conn = get_db()
    cur = conn.cursor()
    
    # First verify that this task belongs to the leader's project
    cur.execute("""
        SELECT t.task_id 
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """, (task_id, leader_id))
    
    task = cur.fetchone()
    
    if not task:
        cur.close()
        conn.close()
        return "Task not found or you don't have permission to delete it", 403
    
    # Delete the task
    cur.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for("project_leader.tasks"))
@project_leader_bp.route("/get_task/<int:task_id>", methods=["GET"])
def get_task(task_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401
    
    leader_id = session["user_id"]
    
    conn = get_db()
    cur = conn.cursor()
    
    # Verify task belongs to leader's project
    cur.execute("""
        SELECT 
            t.task_id,
            t.title,
            t.description,
            t.assigned_to,
            t.project_id,
            t.priority,
            t.status,
            t.due_date
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """, (task_id, leader_id))
    
    task = cur.fetchone()
    cur.close()
    conn.close()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Format the response
    task_data = {
        'task_id': task[0],
        'title': task[1],
        'description': task[2],
        'assigned_to': task[3],
        'project_id': task[4],
        'priority': task[5],
        'status': task[6],
        'due_date': task[7].strftime('%Y-%m-%d') if task[7] else None
    }
    
    return jsonify(task_data)

@project_leader_bp.route("/update_task/<int:task_id>", methods=["POST"])
def update_task(task_id):
    if "user_id" not in session:
        return "Login required"
    
    leader_id = session["user_id"]
    
    title = request.form["title"]
    description = request.form.get("description", "")
    assigned_to = int(request.form["assigned_to"])
    project_id = int(request.form["project_id"])
    priority = request.form["priority"]
    status = request.form["status"]
    due_date = request.form.get("due_date")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Verify task belongs to leader's project
    cur.execute("""
        SELECT t.task_id 
        FROM tasks t
        JOIN projects p ON t.project_id = p.project_id
        WHERE t.task_id = %s AND p.leader_id = %s
    """, (task_id, leader_id))
    
    task = cur.fetchone()
    
    if not task:
        cur.close()
        conn.close()
        return "Task not found or you don't have permission to update it", 403
    
    # Update the task
    cur.execute("""
        UPDATE tasks 
        SET title = %s, 
            description = %s, 
            assigned_to = %s, 
            project_id = %s, 
            priority = %s, 
            status = %s, 
            due_date = %s
        WHERE task_id = %s
    """, (title, description, assigned_to, project_id, priority, status, due_date, task_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for("project_leader.tasks"))

@project_leader_bp.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    leader_id = session["user_id"]
    
    name = request.form.get("name")
    email = request.form.get("email")
    designation = request.form.get("designation")
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Update only existing columns
        cur.execute("""
            UPDATE users 
            SET name = %s,
                email = %s,
                designation = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id;
        """, (name, email, designation, leader_id))
        
        updated = cur.fetchone()
        
        if not updated:
            conn.rollback()
            return jsonify({"success": False, "error": "User not found"}), 404
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully!"
        })
        
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
    
    # Validate
    if not current_password or not new_password or not confirm_password:
        return jsonify({"success": False, "error": "All fields are required"}), 400
    
    if new_password != confirm_password:
        return jsonify({"success": False, "error": "New passwords do not match"}), 400
    
    if len(new_password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verify current password
        cur.execute("""
            SELECT password_hash FROM auth WHERE user_id = %s;
        """, (leader_id,))
        
        auth_data = cur.fetchone()
        
        if not auth_data:
            return jsonify({"success": False, "error": "User authentication not found"}), 404
        
        if auth_data[0] != current_password:  # This should be password hash verification
            return jsonify({"success": False, "error": "Current password is incorrect"}), 400
        
        # Update password
        cur.execute("""
            UPDATE auth 
            SET password_hash = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """, (new_password, leader_id))  # Hash the password before storing!
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully!"
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()