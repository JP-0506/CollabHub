from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    jsonify,
    redirect,
)
from database.db import get_db

auth_bp = Blueprint("auth", __name__)


# -----------------------------
# LOGIN ROUTE (JSON API)
# -----------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # GET Request: લોગિન પેજ બતાવો
    if request.method == "GET":
        return render_template("auth/login.html")

    # POST Request: ડેટા પ્રોસેસ કરો (AJAX)
    if request.method == "POST":
        try:
            # Frontend માંથી JSON ડેટા મેળવો
            data = request.get_json()
            email_or_username = data.get("email", "").strip()
            password = data.get("password", "").strip()

            # 1. Empty Check (જો ખાલી હોય તો)
            if not email_or_username or not password:
                return jsonify({"success": False, "message": "Please fill all fields"})

            conn = get_db()
            cur = conn.cursor()

            # 2. Database Query (PostgreSQL Syntax)
            cur.execute(
                """
                SELECT u.user_id, u.role, a.password_hash, u.is_active, u.is_registered
                FROM users u
                JOIN auth a ON u.user_id = a.user_id
                WHERE u.email = %s OR u.username = %s
                """,
                (email_or_username, email_or_username),
            )

            user = cur.fetchone()
            cur.close()
            conn.close()

            # 3. User Not Found Check
            if not user:
                return jsonify(
                    {
                        "success": False,
                        "message": "You are not registered",
                        "error_type": "user",
                    }
                )

            # ડેટા છૂટો પાડો (Unpack)
            user_id, role, db_password, active, registered = user

            # 4. Registration Check
            if not registered:
                return jsonify(
                    {
                        "success": False,
                        "message": "Activate Your account First",
                        "error_type": "status",
                    }
                )

            # 5. Active Check
            if not active:
                return jsonify(
                    {
                        "success": False,
                        "message": "Account blocked ❌",
                        "error_type": "status",
                    }
                )

            # 6. Password Check (Plain Text Comparison)
            # TOOD
            # =========================================
            # TODO (FUTURE IMPROVEMENT):
            # Replace plain password check with hashing

            if db_password != password:
                return jsonify(
                    {
                        "success": False,
                        "message": "Password wrong",
                        "error_type": "password",
                    }
                )

            # --- LOGIN SUCCESS ---
            session["user_id"] = user_id
            session["role"] = role

            # 7. Role મુજબ Redirect URL નક્કી કરો
            if role == "admin":
                redirect_url = url_for("admin.dashboard")

            elif role == "project_leader":
                redirect_url = url_for("project_leader.dashboard")

            elif role == "employee":
                redirect_url = url_for("employee_dashboard")

            else:
                redirect_url = url_for("home")

            return jsonify(
                {
                    "success": True,
                    "message": "Login Successful!",
                    "redirect_url": redirect_url,
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            raise e
            return jsonify({"success": False, "message": "Server Error"})


# -----------------------------
# SIGNUP / ACTIVATE ACCOUNT
# -----------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():

    # ---------------- GET PAGE of signup----------------
    if request.method == "GET":
        return render_template("auth/signup.html")

    # POST: ડેટા પ્રોસેસ કરો
    if request.method == "POST":
        try:
            data = request.get_json()

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            confirm_password = data.get("confirm_password")

            # Password length check

            # 1️⃣ Basic validation Empty check (FIRST)
            if not all([username, email, password, confirm_password]):
                return jsonify({"success": False, "message": "All fields are required"})

            # 2️⃣ Password length
            if len(password) < 8:
                return jsonify(
                    {
                        "success": False,
                        "message": "Password must be at least 8 characters",
                    }
                )

            # 3️⃣ Match check
            if password != confirm_password:
                return jsonify({"success": False, "message": "Passwords do not match"})

            conn = get_db()
            cur = conn.cursor()

            # 4️⃣ Check user exists & not registered
            cur.execute(
                """
                SELECT user_id, role, is_active, is_registered
                FROM users
                WHERE email = %s
            """,
                (email,),
            )

            user = cur.fetchone()

            if not user:
                cur.close()
                conn.close()
                return jsonify(
                    {"success": False, "message": "You are not registered by admin"}
                )

            user_id, role, is_active, is_registered = user

            if not is_active:
                cur.close()
                conn.close()
                return jsonify({"success": False, "message": "Your account is blocked"})

            if is_registered:
                cur.close()
                conn.close()
                return jsonify(
                    {"success": False, "message": "Account already activated"}
                )

            # 5️⃣ Check username exists for to prevents duplication
            cur.execute(
                """
                SELECT user_id FROM users
                WHERE username = %s
            """,
                (username,),
            )

            if cur.fetchone():
                cur.close()
                conn.close()

                return jsonify({"success": False, "message": "Username already taken"})

            # 6️⃣ Insert password (PLAIN for now)
            cur.execute(
                """
                INSERT INTO auth (user_id, password_hash, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
            """,
                (user_id, password),
            )

            # 7️⃣ Update users table
            cur.execute(
                """
                UPDATE users
                SET username = %s,
                    is_registered = TRUE
                WHERE user_id = %s
            """,
                (username, user_id),
            )

            conn.commit()
            cur.close()
            conn.close()

            # 8️⃣ Set Session (AUTO LOGIN)
            session["user_id"] = user_id
            session["role"] = role

            # 9️⃣ Decide redirect
            if role == "admin":
                redirect_url = url_for("admin.admin_home")

            elif role == "project_leader":
                 redirect_url = url_for("project_leader.dashboard")

            elif role == "employee":
                redirect_url = url_for("employee_dashboard")
            else:
                redirect_url = url_for("home")

            cur.close()
            conn.close()

            # 🔟 Send response
            return jsonify(
                {
                    "success": True,
                    "message": "Account activated successfully",
                    "redirect_url": redirect_url,
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            raise e  # for print error in console
            # જો કોઈ બીજી એરર આવે (જેમ કે user_id already exists in auth)
            return jsonify(
                {"success": False, "message": "Registration Failed or Server Error"}
            )


@auth_bp.route("/forgotPassword", methods=["GET", "POST"])
def forgotPassword():

    return render_template("auth/forgotPassword.html")
