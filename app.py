from flask import Flask, render_template, redirect, session, url_for

from auth import auth_bp
from admin import admin_bp
from leader.routes import project_leader_bp
from employee.routes import employee_bp

app = Flask(__name__)

app.secret_key = "collabhub_secret_key"
from flask_mail import Mail, Message

# Mail configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"  # or your SMTP server
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "sharingcode14@gmail.com"
app.config["MAIL_PASSWORD"] = "dxrv rxio jafe fcnm"
app.config["MAIL_DEFAULT_SENDER"] = "sharingcode14@gmail.com"

mail = Mail(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(project_leader_bp, url_prefix="/projectleader")
app.register_blueprint(employee_bp, url_prefix="/employee")


# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")


# LOGOUT
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# RUN

if __name__ == "__main__":
    app.run(debug=True)


@app.context_processor
def inject_user():
    if "user_id" in session:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT name, role FROM users WHERE user_id = %s", (session["user_id"],)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return dict(current_user={"name": user[0], "role": user[1]})
    return dict(current_user=None)
