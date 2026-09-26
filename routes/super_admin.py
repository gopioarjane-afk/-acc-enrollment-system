from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from auth_helpers import role_required
from database.db import query_db, execute_db

super_admin_bp = Blueprint("super_admin", __name__, url_prefix="/super-admin")

@super_admin_bp.route("/dashboard")
@role_required("super_admin")
def dashboard():
    stats = {
        "users": query_db("SELECT COUNT(*) AS c FROM users", one=True)["c"],
        "admins": query_db("SELECT COUNT(*) AS c FROM users WHERE role='admin'", one=True)["c"],
        "students": query_db("SELECT COUNT(*) AS c FROM students", one=True)["c"],
        "pending": query_db(
            "SELECT COUNT(*) AS c FROM enrollments WHERE status='Pending'", one=True
        )["c"],
    }
    return render_template("super_admin/dashboard.html", stats=stats)

@super_admin_bp.route("/admins", methods=["GET", "POST"])
@role_required("super_admin")
def admins():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not full_name or not password:
            flash("Username, full name, and password are required.", "danger")
        else:
            try:
                execute_db(
                    """INSERT INTO users
                       (username, password_hash, full_name, email, role)
                       VALUES (?, ?, ?, ?, 'admin')""",
                    (username, generate_password_hash(password), full_name, email),
                )
                flash("Admin account created.", "success")
            except Exception as e:
                flash(f"Could not create admin: {e}", "danger")

        return redirect(url_for("super_admin.admins"))

    admins = query_db(
        """SELECT id, username, full_name, email, is_active, created_at
           FROM users WHERE role='admin' ORDER BY id DESC"""
    )
    return render_template("super_admin/admins.html", admins=admins)

@super_admin_bp.route("/users")
@role_required("super_admin")
def users():
    users = query_db(
        """SELECT id, username, full_name, email, role, is_active, created_at
           FROM users ORDER BY id DESC"""
    )
    return render_template("super_admin/users.html", users=users)

@super_admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@role_required("super_admin")
def toggle_user(user_id):
    if user_id == 1:
        flash("The default Super Admin cannot be disabled.", "warning")
        return redirect(url_for("super_admin.users"))

    execute_db(
        "UPDATE users SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?",
        (user_id,),
    )
    flash("User status updated.", "success")
    return redirect(url_for("super_admin.users"))
