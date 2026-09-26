from flask import Flask, render_template, redirect, url_for, session, flash
from config import Config
from database.db import init_db
from auth_helpers import login_required

app = Flask(__name__)
app.config.from_object(Config)


@app.context_processor
def inject_user():
    return {
        "current_user": {
            "id": session.get("user_id"),
            "name": session.get("full_name"),
            "username": session.get("username"),
            "role": session.get("role"),
        }
    }


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))


@app.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")

    if role == "super_admin":
        return redirect(url_for("super_admin.dashboard"))

    if role == "admin":
        return redirect(url_for("admin.dashboard"))

    return redirect(url_for("student.dashboard"))


from routes.auth import auth_bp
from routes.super_admin import super_admin_bp
from routes.admin import admin_bp
from routes.student import student_bp


app.register_blueprint(auth_bp)
app.register_blueprint(super_admin_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)


if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(debug=True, host="127.0.0.1", port=5000)