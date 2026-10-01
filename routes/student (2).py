from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from auth_helpers import role_required
from database.db import get_db


student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/student"
)


@student_bp.route("/dashboard")
@role_required("student")
def dashboard():
    db = get_db()

    student = db.execute(
        """
        SELECT
            s.*,
            u.username,
            u.email
        FROM students s
        JOIN users u ON u.id = s.user_id
        WHERE s.user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    enrollment = None

    if student:
        enrollment = db.execute(
            """
            SELECT
                e.*,
                p.program_code,
                p.program_name
            FROM enrollments e
            JOIN programs p ON p.id = e.program_id
            WHERE e.student_id = ?
            ORDER BY e.id DESC
            LIMIT 1
            """,
            (student["id"],)
        ).fetchone()

    db.close()

    return render_template(
        "student/dashboard.html",
        student=student,
        enrollment=enrollment
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@role_required("student")
def profile():
    db = get_db()

    student = db.execute(
        """
        SELECT
            s.*,
            u.username,
            u.email
        FROM students s
        JOIN users u ON u.id = s.user_id
        WHERE s.user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if student is None:
        db.close()
        flash("Student profile not found.", "danger")
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        middle_name = request.form.get("middle_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        birthdate = request.form.get("birthdate", "").strip()
        gender = request.form.get("gender", "").strip()
        address = request.form.get("address", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        if not first_name or not last_name:
            flash(
                "First name and last name are required.",
                "danger"
            )
            db.close()

            return render_template(
                "student/profile.html",
                student=student
            )

        db.execute(
            """
            UPDATE students
            SET
                first_name = ?,
                middle_name = ?,
                last_name = ?,
                birthdate = ?,
                gender = ?,
                address = ?,
                phone = ?
            WHERE user_id = ?
            """,
            (
                first_name,
                middle_name,
                last_name,
                birthdate,
                gender,
                address,
                phone,
                session["user_id"]
            )
        )

        db.execute(
            """
            UPDATE users
            SET
                full_name = ?,
                email = ?
            WHERE id = ?
            """,
            (
                f"{first_name} {last_name}",
                email,
                session["user_id"]
            )
        )

        db.commit()
        db.close()

        session["full_name"] = f"{first_name} {last_name}"

        flash("Profile updated successfully.", "success")

        return redirect(url_for("student.profile"))

    db.close()

    return render_template(
        "student/profile.html",
        student=student
    )


@student_bp.route("/enrollment", methods=["GET", "POST"])
@role_required("student")
def enrollment():
    db = get_db()

    student = db.execute(
        """
        SELECT id
        FROM students
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if student is None:
        db.close()
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("student.profile"))

    programs = db.execute(
        """
        SELECT *
        FROM programs
        WHERE status = 'active'
        ORDER BY program_name
        """
    ).fetchall()

    if request.method == "POST":
        program_id = request.form.get("program_id")
        school_year = request.form.get("school_year", "").strip()
        semester = request.form.get("semester", "").strip()

        if not program_id or not school_year or not semester:
            flash(
                "Please complete all enrollment fields.",
                "danger"
            )
        else:
            try:
                db.execute(
                    """
                    INSERT INTO enrollments
                    (
                        student_id,
                        program_id,
                        school_year,
                        semester,
                        status
                    )
                    VALUES (?, ?, ?, ?, 'Pending')
                    """,
                    (
                        student["id"],
                        program_id,
                        school_year,
                        semester
                    )
                )

                db.commit()

                flash(
                    "Enrollment submitted successfully.",
                    "success"
                )

                db.close()

                return redirect(
                    url_for("student.dashboard")
                )

            except Exception:
                db.rollback()

                flash(
                    "Unable to submit enrollment.",
                    "danger"
                )

    db.close()

    return render_template(
        "student/enrollment.html",
        programs=programs
    )