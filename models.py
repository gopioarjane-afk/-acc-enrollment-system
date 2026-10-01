from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # super_admin, admin, student
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship(
        "StudentProfile", back_populates="user", uselist=False,
        cascade="all, delete-orphan"
    )
    enrollments = db.relationship(
        "Enrollment", back_populates="student",
        foreign_keys="Enrollment.student_id",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    program = db.Column(db.String(150), nullable=False)
    year_level = db.Column(db.String(30), nullable=False)
    contact_number = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", back_populates="student_profile")


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    units = db.Column(db.Integer, nullable=False, default=3)
    instructor = db.Column(db.String(150), nullable=True)
    schedule = db.Column(db.String(150), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=40)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    enrollments = db.relationship(
        "Enrollment", back_populates="course",
        cascade="all, delete-orphan"
    )


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    school_year = db.Column(db.String(30), nullable=False)
    semester = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    student = db.relationship(
        "User", back_populates="enrollments",
        foreign_keys=[student_id]
    )
    course = db.relationship("Course", back_populates="enrollments")
    approver = db.relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        db.UniqueConstraint(
            "student_id", "course_id", "school_year", "semester",
            name="uq_student_course_term"
        ),
    )
