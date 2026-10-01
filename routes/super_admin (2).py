from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from auth_helpers import role_required
from database.db import get_db


super_admin_bp = Blueprint(
    "super_admin",
    __name__,
    url_prefix="/super-admin"
)


@super_admin_bp.route("/dashboard")
@role_required("super_admin")
def dashboard():
    db = get_db()

    total_users = db.execute(
        "SELECT COUNT(*) AS total FROM users"
    ).fetchone()["total"]

    total_admins = db.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'admin'"
    ).fetchone()["total"]

    total_students = db.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'student'"
    ).fetchone()["total"]

    total_enrollments = db.execute(
        "SELECT COUNT(*) AS total FROM enrollments"
    ).fetchone()["total"]

    db.close()

    return render_template(
        "super_admin/dashboard.html",
        total_users=total_users,
        total_admins=total_admins,
        total_students=total_students,
        total_enrollments=total_enrollments
    )


@super_admin_bp.route("/admins")
@role_required("super_admin")
def admins():
    db = get_db()

    admins = db.execute(
        """
        SELECT id, username, full_name, email, status, created_at
        FROM users
        WHERE role = 'admin'
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "super_admin/admins.html",
        admins=admins
    )


@super_admin_bp.route("/admins/create", methods=["POST"])
@role_required("super_admin")
def create_admin():
    username = request.form.get("username", "").strip()
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not username or not full_name or not password:
        flash(
            "Username, full name, and password are required.",
            "danger"
        )
        return redirect(url_for("super_admin.admins"))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO users
            (username, password, full_name, email, role, status)
            VALUES (?, ?, ?, ?, 'admin', 'active')
            """,
            (
                username,
                generate_password_hash(password),
                full_name,
                email
            )
        )

        db.commit()
        flash("Admin account created successfully.", "success")

    except Exception:
        db.rollback()
        flash("Username may already exist.", "danger")

    finally:
        db.close()

    return redirect(url_for("super_admin.admins"))


@super_admin_bp.route("/users")
@role_required("super_admin")
def users():
    db = get_db()

    users = db.execute(
        """
        SELECT id, username, full_name, email, role, status, created_at
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "super_admin/users.html",
        users=users
    )


@super_admin_bp.route("/programs", methods=["GET", "POST"])
@role_required("super_admin")
def programs():
    db = get_db()

    if request.method == "POST":
        code = request.form.get("program_code", "").strip()
        name = request.form.get("program_name", "").strip()
        description = request.form.get("description", "").strip()

        if not code or not name:
            flash(
                "Program code and program name are required.",
                "danger"
            )
        else:
            try:
                db.execute(
                    """
                    INSERT INTO programs
                    (program_code, program_name, description)
                    VALUES (?, ?, ?)
                    """,
                    (code, name, description)
                )

                db.commit()
                flash("Program added successfully.", "success")

            except Exception:
                db.rollback()
                flash("Program code may already exist.", "danger")

    programs = db.execute(
        """
        SELECT *
        FROM programs
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "super_admin/programs.html",
        programs=programs
    )