from flask import Flask, render_template, session, redirect, url_for

from config import Config
from database.db import init_db
from auth_helpers import login_required

from routes.auth import auth_bp
from routes.super_admin import super_admin_bp
from routes.admin import admin_bp
from routes.student import student_bp


app = Flask(__name__)
app.config.from_object(Config)


# Register route blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(super_admin_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)


@app.context_processor
def inject_user():
    return {
        "current_user": {
            "id": session.get("user_id"),
            "username": session.get("username"),
            "full_name": session.get("full_name"),
            "role": session.get("role")
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

    if role == "student":
        return redirect(url_for("student.dashboard"))

    session.clear()

    return redirect(url_for("auth.login"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "error.html",
        error_code=404,
        message="Page not found."
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        "error.html",
        error_code=500,
        message="Internal server error."
    ), 500


if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )