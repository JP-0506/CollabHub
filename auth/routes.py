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

# below for the forget pass
import random
import secrets
from datetime import datetime, timedelta
from flask_mail import Message
from flask import current_app

# *************/

auth_bp = Blueprint("auth", __name__)


# -----------------------------
# LOGIN ROUTE (JSON API)
# -----------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # GET → show login page
    if request.method == "GET":
        return render_template("auth/login.html")

    # POST → process login
    if request.method == "POST":
        try:

            data = request.get_json()

            email_or_username = data.get("email", "").strip()
            password = data.get("password", "").strip()

            # Empty check
            if not email_or_username or not password:
                return jsonify({"success": False, "message": "Please fill all fields"})

            conn = get_db()
            cur = conn.cursor()

            # Fetch user INCLUDING NAME
            cur.execute(
                """
                SELECT 
                    u.user_id,
                    u.name,
                    u.role,
                    a.password_hash,
                    u.is_active,
                    u.is_registered
                FROM users u
                JOIN auth a ON u.user_id = a.user_id
                WHERE u.email = %s OR u.username = %s
            """,
                (email_or_username, email_or_username),
            )

            user = cur.fetchone()

            cur.close()
            conn.close()

            # User not found
            if not user:
                return jsonify(
                    {
                        "success": False,
                        "message": "You are not registered",
                        "error_type": "user",
                    }
                )

            # CORRECT unpack
            user_id, name, role, db_password, active, registered = user

            # Registration check
            if not registered:
                return jsonify(
                    {
                        "success": False,
                        "message": "Activate Your account First",
                        "error_type": "status",
                    }
                )

            # Active check
            if not active:
                return jsonify(
                    {
                        "success": False,
                        "message": "Account blocked ❌",
                        "error_type": "status",
                    }
                )

            # Password check
            if db_password != password:
                return jsonify(
                    {
                        "success": False,
                        "message": "Password wrong",
                        "error_type": "password",
                    }
                )

            # ✅ LOGIN SUCCESS
            session.clear()

            session["user_id"] = user_id
            session["name"] = name  # THIS FIXES SIDEBAR
            session["role"] = role
            session["username"] = email_or_username

            # 📝 Log login info into login_logs table
            try:
                log_conn = get_db()
                log_cur = log_conn.cursor()

                log_cur.execute(
                    """
                    INSERT INTO login_logs (user_id, login_time)
                    VALUES (%s, CURRENT_TIMESTAMP)
                    """,
                    (user_id,),
                )
                log_conn.commit()
                log_cur.close()
                log_conn.close()
            except Exception as log_err:
                print("LOGIN LOG ERROR:", log_err)

            # Redirect based on role
            if role == "admin":
                redirect_url = url_for("admin.dashboard")

            elif role == "project_leader":
                redirect_url = url_for("project_leader.dashboard")

            elif role == "employee":
                redirect_url = url_for("employee.dashboard")

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

            print("LOGIN ERROR:", e)

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
                redirect_url = url_for("employee.dashboard")
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


# /*********forgot

# -----------------------------
# SEND OTP
# -----------------------------


@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    try:
        data = request.get_json()
        email = data.get("email", "").strip()

        if not email:
            return jsonify({"success": False, "message": "Please enter your email"})

        conn = get_db()
        cur = conn.cursor()

        # Check if email exists
        cur.execute(
            """
            SELECT u.user_id, u.is_registered, u.is_active, u.name
            FROM users u
            WHERE u.email = %s
            """,
            (email,),
        )

        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Email not found"})

        user_id, is_registered, is_active, name = user

        if not is_registered:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Account not activated"})

        if not is_active:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Account is blocked"})

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        otp_expires = datetime.now() + timedelta(minutes=5)

        # Create Email Message
        msg = Message(
            subject="CollabHub - Password Reset OTP",
            recipients=[email],
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        )

        msg.body = f"""
        CollabHub - Password Reset OTP

        Hello {name},

        Your OTP for password reset is: {otp_code}

        This OTP is valid for 5 minutes.

        If you didn't request this, please ignore this email.
        """

        msg.html = f"""
        <html>
        <body>
            <h2>CollabHub - Password Reset OTP</h2>
            <p>Hello {name},</p>
            <p>Your OTP for password reset is: <strong>{otp_code}</strong></p>
            <p>This OTP is valid for 5 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The CollabHub Team</p>
        </body>
        </html>
        """

        try:
            mail = current_app.extensions["mail"]
            mail.send(msg)
            email_sent = True
            print(f"OTP email sent successfully to {email}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            email_sent = False

        # Store OTP in session
        session["otp_code"] = otp_code
        session["otp_email"] = email
        session["otp_expires"] = otp_expires.timestamp()

        cur.close()
        conn.close()

        if email_sent:
            return jsonify(
                {"success": True, "message": "OTP has been sent to your email"}
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": f"Email sending failed. OTP: {otp_code} (Check console)",
                    "debug_otp": otp_code,
                }
            )

    except Exception as e:
        print(f"Error in send_otp: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "message": "Server error"})


# -----------------------------
# VERIFY OTP
# -----------------------------
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get("email", "").strip()
        otp = data.get("otp", "").strip()

        if not email or not otp:
            return jsonify({"success": False, "message": "Email and OTP required"})

        # Check session OTP
        if (
            "otp_email" not in session
            or "otp_code" not in session
            or "otp_expires" not in session
        ):
            return jsonify({"success": False, "message": "No OTP requested"})

        if session["otp_email"] != email:
            return jsonify({"success": False, "message": "Invalid request"})

        # Check expiration
        if datetime.now().timestamp() > session["otp_expires"]:
            return jsonify({"success": False, "message": "OTP expired"})

        # Verify OTP
        if session["otp_code"] != otp:
            return jsonify({"success": False, "message": "Invalid OTP"})

        # OTP verified - generate reset token
        reset_token = secrets.token_hex(32)
        session["reset_token"] = reset_token
        session["reset_email"] = email

        # Clear OTP from session
        session.pop("otp_code", None)
        session.pop("otp_email", None)
        session.pop("otp_expires", None)

        reset_url = url_for("auth.reset_password", token=reset_token, _external=True)

        return jsonify(
            {"success": True, "message": "OTP verified!", "reset_url": reset_url}
        )

    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({"success": False, "message": "Server error"})


# -----------------------------
# RESET PASSWORD (with token from OTP verification)
# -----------------------------
@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # GET: Show reset password form
    if request.method == "GET":
        # Verify token
        if (
            "reset_token" not in session
            or session["reset_token"] != token
            or "reset_email" not in session
        ):
            return "Invalid or expired reset link", 400

        email = session["reset_email"]
        return render_template("auth/reset_password.html", token=token, email=email)

    # POST: Process password reset
    if request.method == "POST":
        try:
            # Verify token
            if "reset_token" not in session or session["reset_token"] != token:
                return jsonify({"success": False, "message": "Invalid token"})

            data = request.get_json()
            new_password = data.get("password", "").strip()
            confirm_password = data.get("confirm_password", "").strip()

            # Validation
            if not new_password or not confirm_password:
                return jsonify({"success": False, "message": "Please fill all fields"})

            if len(new_password) < 8:
                return jsonify(
                    {
                        "success": False,
                        "message": "Password must be at least 8 characters",
                    }
                )

            if new_password != confirm_password:
                return jsonify({"success": False, "message": "Passwords do not match"})

            email = session["reset_email"]

            conn = get_db()
            cur = conn.cursor()

            # Get user_id from email
            cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))

            user = cur.fetchone()
            if not user:
                cur.close()
                conn.close()
                return jsonify({"success": False, "message": "User not found"})

            user_id = user[0]

            # Update password
            cur.execute(
                """
                UPDATE auth 
                SET password_hash = %s, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """,
                (new_password, user_id),
            )

            conn.commit()
            cur.close()
            conn.close()

            # Clear reset session
            session.pop("reset_token", None)
            session.pop("reset_email", None)

            return jsonify(
                {
                    "success": True,
                    "message": "Password reset successful!",
                    "redirect_url": url_for("auth.login"),
                }
            )

        except Exception as e:
            print(f"Error in reset_password: {e}")
            return jsonify({"success": False, "message": "Server error"})
