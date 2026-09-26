from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from auth_helpers import role_required
from database.db import query_db, execute_db

student_bp = Blueprint("student", __name__, url_prefix="/student")

def get_current_student():
    return query_db(
        """SELECT s.*, u.username, u.email
           FROM students s JOIN users u ON u.id=s.user_id
           WHERE s.user_id=?""",
        (session["user_id"],),
        one=True,
    )

@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    student = get_current_student()
    enrollments = []
    if student:
        enrollments = query_db(
            """SELECT * FROM enrollments
               WHERE student_id=? ORDER BY id DESC""",
            (student["id"],),
        )
    return render_template(
        "student/dashboard.html",
        student=student,
        enrollments=enrollments,
    )

@student_bp.route("/profile", methods=["GET", "POST"])
@role_required("student")
def profile():
    student = get_current_student()

    if request.method == "POST":
        data = (
            request.form.get("first_name", "").strip(),
            request.form.get("middle_name", "").strip(),
            request.form.get("last_name", "").strip(),
            request.form.get("birth_date", "").strip(),
            request.form.get("sex", "").strip(),
            request.form.get("address", "").strip(),
            request.form.get("phone", "").strip(),
            request.form.get("course", "").strip(),
            request.form.get("year_level", "").strip(),
            student["id"],
        )

        execute_db(
            """UPDATE students
               SET first_name=?, middle_name=?, last_name=?, birth_date=?,
                   sex=?, address=?, phone=?, course=?, year_level=?
               WHERE id=?""",
            data,
        )

        email = request.form.get("email", "").strip()
        execute_db(
            "UPDATE users SET email=? WHERE id=?",
            (email, session["user_id"]),
        )

        session["full_name"] = (
            f"{data[0]} {data[1] + ' ' if data[1] else ''}{data[2]}"
        ).strip()

        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)

@student_bp.route("/enrollment", methods=["GET", "POST"])
@role_required("student")
def enrollment():
    student = get_current_student()
    if not student:
        flash("Please complete your student profile first.", "warning")
        return redirect(url_for("student.profile"))

    if request.method == "POST":
        school_year = request.form.get("school_year", "").strip()
        semester = request.form.get("semester", "").strip()

        if not school_year or not semester:
            flash("School year and semester are required.", "danger")
        else:
            execute_db(
                """INSERT INTO enrollments
                   (student_id, school_year, semester, status)
                   VALUES (?, ?, ?, 'Pending')""",
                (student["id"], school_year, semester),
            )
            flash("Enrollment submitted successfully.", "success")
            return redirect(url_for("student.dashboard"))

    return render_template("student/enrollment.html", student=student)
