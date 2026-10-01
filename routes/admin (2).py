from flask import Blueprint, flash, redirect, render_template, request, url_for

from auth_helpers import role_required
from database.db import get_db


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    db = get_db()

    total_students = db.execute(
        "SELECT COUNT(*) AS total FROM users WHERE role = 'student'"
    ).fetchone()["total"]

    pending_enrollments = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM enrollments
        WHERE status = 'Pending'
        """
    ).fetchone()["total"]

    approved_enrollments = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM enrollments
        WHERE status = 'Approved'
        """
    ).fetchone()["total"]

    rejected_enrollments = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM enrollments
        WHERE status = 'Rejected'
        """
    ).fetchone()["total"]

    db.close()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        pending_enrollments=pending_enrollments,
        approved_enrollments=approved_enrollments,
        rejected_enrollments=rejected_enrollments
    )


@admin_bp.route("/students")
@role_required("admin")
def students():
    db = get_db()

    students = db.execute(
        """
        SELECT
            s.id,
            s.student_id,
            s.first_name,
            s.middle_name,
            s.last_name,
            s.birthdate,
            s.gender,
            s.phone,
            u.username,
            u.email,
            u.status
        FROM students s
        JOIN users u ON u.id = s.user_id
        ORDER BY s.id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin/students.html",
        students=students
    )


@admin_bp.route("/students/<int:student_id>")
@role_required("admin")
def student_view(student_id):
    db = get_db()

    student = db.execute(
        """
        SELECT
            s.*,
            u.username,
            u.email,
            u.status
        FROM students s
        JOIN users u ON u.id = s.user_id
        WHERE s.id = ?
        """,
        (student_id,)
    ).fetchone()

    if student is None:
        db.close()
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))

    enrollments = db.execute(
        """
        SELECT
            e.*,
            p.program_code,
            p.program_name
        FROM enrollments e
        JOIN programs p ON p.id = e.program_id
        WHERE e.student_id = ?
        ORDER BY e.id DESC
        """,
        (student_id,)
    ).fetchall()

    db.close()

    return render_template(
        "admin/student_view.html",
        student=student,
        enrollments=enrollments
    )


@admin_bp.route("/enrollments")
@role_required("admin")
def enrollments():
    db = get_db()

    enrollments = db.execute(
        """
        SELECT
            e.id,
            e.school_year,
            e.semester,
            e.status,
            e.remarks,
            e.submitted_at,
            e.reviewed_at,
            s.student_id,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name
        FROM enrollments e
        JOIN students s ON s.id = e.student_id
        JOIN programs p ON p.id = e.program_id
        ORDER BY e.id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "admin/enrollments.html",
        enrollments=enrollments
    )


@admin_bp.route(
    "/enrollments/<int:enrollment_id>/review",
    methods=["POST"]
)
@role_required("admin")
def review_enrollment(enrollment_id):
    action = request.form.get("action", "").strip()
    remarks = request.form.get("remarks", "").strip()

    if action not in ("Approved", "Rejected"):
        flash("Invalid enrollment action.", "danger")
        return redirect(url_for("admin.enrollments"))

    db = get_db()

    enrollment = db.execute(
        """
        SELECT id
        FROM enrollments
        WHERE id = ?
        """,
        (enrollment_id,)
    ).fetchone()

    if enrollment is None:
        db.close()
        flash("Enrollment not found.", "danger")
        return redirect(url_for("admin.enrollments"))

    db.execute(
        """
        UPDATE enrollments
        SET
            status = ?,
            remarks = ?,
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = ?
        WHERE id = ?
        """,
        (
            action,
            remarks,
            request_user_id(),
            enrollment_id
        )
    )

    db.commit()
    db.close()

    flash(
        f"Enrollment has been {action.lower()}.",
        "success"
    )

    return redirect(url_for("admin.enrollments"))


def request_user_id():
    from flask import session
    return session.get("user_id")