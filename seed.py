from app import app
from werkzeug.security import generate_password_hash
from database.db import execute_db, query_db

def main():
    with app.app_context():
        # Creates one demo Admin account.
        existing = query_db("SELECT id FROM users WHERE username=?", ("admin",), one=True)
        if not existing:
            execute_db(
                """INSERT INTO users
                   (username,password_hash,full_name,email,role)
                   VALUES (?,?,?,?,?)""",
                (
                    "admin",
                    generate_password_hash("Admin123!"),
                    "Demo Administrator",
                    "admin@example.com",
                    "admin",
                ),
            )
            print("Created admin: admin / Admin123!")
        else:
            print("Admin account already exists.")

        # Creates one demo Student account and student profile.
        existing = query_db("SELECT id FROM users WHERE username=?", ("student",), one=True)
        if not existing:
            user_id = execute_db(
                """INSERT INTO users
                   (username,password_hash,full_name,email,role)
                   VALUES (?,?,?,?,?)""",
                (
                    "student",
                    generate_password_hash("Student123!"),
                    "Juan Dela Cruz",
                    "student@example.com",
                    "student",
                ),
            )
            execute_db(
                """INSERT INTO students
                   (user_id,student_number,first_name,middle_name,last_name,
                    course,year_level)
                   VALUES (?,?,?,?,?,?,?)""",
                (
                    user_id,
                    "2026-0001",
                    "Juan",
                    "Dela",
                    "Cruz",
                    "BS Information Technology",
                    "1st Year",
                ),
            )
            print("Created student: student / Student123!")
        else:
            print("Student account already exists.")

if __name__ == "__main__":
    main()
