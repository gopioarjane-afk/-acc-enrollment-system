from werkzeug.security import generate_password_hash

from app import app
from database.db import get_db, init_db


def seed_database():
    with app.app_context():

        # Create database tables
        init_db()

        db = get_db()

        # ==========================================
        # SUPER ADMIN
        # ==========================================

        super_admin = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            ("superadmin",)
        ).fetchone()

        if not super_admin:

            db.execute(
                """
                INSERT INTO users
                (
                    username,
                    password,
                    full_name,
                    email,
                    role,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "superadmin",
                    generate_password_hash("SuperAdmin123!"),
                    "ACC Super Administrator",
                    "superadmin@acc.edu.ph",
                    "super_admin",
                    "active"
                )
            )

            print("Super Admin account created.")


        # ==========================================
        # ADMIN
        # ==========================================

        admin = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            ("admin",)
        ).fetchone()

        if not admin:

            db.execute(
                """
                INSERT INTO users
                (
                    username,
                    password,
                    full_name,
                    email,
                    role,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "admin",
                    generate_password_hash("Admin123!"),
                    "ACC Administrator",
                    "admin@acc.edu.ph",
                    "admin",
                    "active"
                )
            )

            print("Admin account created.")


        # ==========================================
        # STUDENT USER
        # ==========================================

        student_user = db.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            ("student",)
        ).fetchone()

        if not student_user:

            cursor = db.execute(
                """
                INSERT INTO users
                (
                    username,
                    password,
                    full_name,
                    email,
                    role,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "student",
                    generate_password_hash("Student123!"),
                    "Juan Dela Cruz",
                    "student@acc.edu.ph",
                    "student",
                    "active"
                )
            )

            student_user_id = cursor.lastrowid

            print("Student account created.")

        else:

            student_user_id = student_user["id"]


        # ==========================================
        # STUDENT PROFILE
        # ==========================================

        student = db.execute(
            """
            SELECT id
            FROM students
            WHERE user_id = ?
            """,
            (student_user_id,)
        ).fetchone()

        if not student:

            db.execute(
                """
                INSERT INTO students
                (
                    user_id,
                    student_id,
                    first_name,
                    middle_name,
                    last_name,
                    birthdate,
                    gender,
                    address,
                    phone
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_user_id,
                    "2026-0001",
                    "Juan",
                    "Dela Cruz",
                    "Student",
                    "2005-01-15",
                    "Male",
                    "Abuyog, Leyte",
                    "09123456789"
                )
            )

            print("Student profile created.")


        # ==========================================
        # SAMPLE PROGRAMS
        # ==========================================

        programs = [
            (
                "BSIT",
                "Bachelor of Science in Information Technology",
                "Program focused on information technology, software, and computer systems."
            ),
            (
                "BSBA",
                "Bachelor of Science in Business Administration",
                "Program focused on business management and administration."
            ),
            (
                "BEED",
                "Bachelor of Elementary Education",
                "Program focused on elementary education and teaching."
            ),
            (
                "BSED",
                "Bachelor of Secondary Education",
                "Program focused on secondary education and teaching."
            )
        ]


        for code, name, description in programs:

            existing_program = db.execute(
                """
                SELECT id
                FROM programs
                WHERE program_code = ?
                """,
                (code,)
            ).fetchone()

            if not existing_program:

                db.execute(
                    """
                    INSERT INTO programs
                    (
                        program_code,
                        program_name,
                        description,
                        status
                    )
                    VALUES (?, ?, ?, 'active')
                    """,
                    (
                        code,
                        name,
                        description
                    )
                )

                print(f"Program created: {code}")


        db.commit()
        db.close()

        print()
        print("==========================================")
        print("DATABASE SEED COMPLETED")
        print("==========================================")
        print()
        print("Super Admin:")
        print("Username: superadmin")
        print("Password: SuperAdmin123!")
        print()
        print("Admin:")
        print("Username: admin")
        print("Password: Admin123!")
        print()
        print("Student:")
        print("Username: student")
        print("Password: Student123!")
        print()
        print("==========================================")


if __name__ == "__main__":
    seed_database()