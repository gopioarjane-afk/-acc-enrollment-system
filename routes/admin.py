from flask import Blueprint, render_template, request, redirect, url_for, flash
from auth_helpers import role_required
from database.db import query_db, execute_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@role_required("admin", "super_admin")
def dashboard():
    stats = {
        "students": query_db("SELECT COUNT(*) AS c FROM students", one=True)["c"],
        "pending": query_db(
            "SELECT COUNT(*) AS c FROM enrollments WHERE status='Pending'", one=True
        )["c"],
        "approved": query_db(
            "SELECT COUNT(*) AS c FROM enrollments WHERE status='Approved'", one=True
        )["c"],
        "rejected": query_db(
            "SELECT COUNT(*) AS c FROM enrollments WHERE status='Rejected'", one=True
        )["c"],
    }
    return render_template("admin/dashboard.html", stats=stats)

@admin_bp.route("/students")
@role_required("admin", "super_admin")
def students():
    keyword = request.args.get("q", "").strip()
    if keyword:
        students = query_db(
            """SELECT s.*, u.username, u.email
               FROM students s JOIN users u ON u.id=s.user_id
               WHERE s.student_number LIKE ?
                  OR s.first_name LIKE ?
                  OR s.last_name LIKE ?
               ORDER BY s.id DESC""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
        )
    else:
        students = query_db(
            """SELECT s.*, u.username, u.email
               FROM students s JOIN users u ON u.id=s.user_id
               ORDER BY s.id DESC"""
        )
    return render_template("admin/students.html", students=students, keyword=keyword)

@admin_bp.route("/students/<int:student_id>")
@role_required("admin", "super_admin")
def student_view(student_id):
    student = query_db(
        """SELECT s.*, u.username, u.email
           FROM students s JOIN users u ON u.id=s.user_id
           WHERE s.id=?""",
        (student_id,),
        one=True,
    )
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))

    enrollments = query_db(
        """SELECT * FROM enrollments
           WHERE student_id=? ORDER BY id DESC""",
        (student_id,),
    )
    return render_template(
        "admin/student_view.html",
        student=student,
        enrollments=enrollments,
    )

@admin_bp.route("/enrollments")
@role_required("admin", "super_admin")
def enrollments():
    enrollments = query_db(
        """SELECT e.*, s.student_number, s.first_name, s.last_name
           FROM enrollments e
           JOIN students s ON s.id=e.student_id
           ORDER BY e.id DESC"""
    )
    return render_template("admin/enrollments.html", enrollments=enrollments)

@admin_bp.route("/enrollments/<int:enrollment_id>/status", methods=["POST"])
@role_required("admin", "super_admin")
def update_enrollment(enrollment_id):
    status = request.form.get("status")
    remarks = request.form.get("remarks", "").strip()

    if status not in ("Pending", "Approved", "Rejected"):
        flash("Invalid enrollment status.", "danger")
        return redirect(url_for("admin.enrollments"))

    execute_db(
        """UPDATE enrollments
           SET status=?, remarks=?, updated_at=CURRENT_TIMESTAMP
           WHERE id=?""",
        (status, remarks, enrollment_id),
    )
    flash("Enrollment updated.", "success")
    return redirect(url_for("admin.enrollments"))
