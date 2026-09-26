# ACC Enrollment System

A complete starter Student Account Enrollment System built with:

- Python
- Flask
- HTML/CSS + Bootstrap
- SQLite
- Role-Based Access Control (RBAC)

## Roles

### Super Admin
- Dashboard
- Create Admin accounts
- View all users
- Enable/disable users
- View students
- Manage enrollment records

### Admin
- Dashboard
- Search/view students
- Review enrollment applications
- Set enrollment status to Pending, Approved, or Rejected
- Add remarks

### Student
- Dashboard
- Edit own profile
- Submit enrollment
- View own enrollment status

## Windows installation

Open PowerShell in this folder.

```powershell
py --version
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python seed.py
python app.py
```

Open:

http://127.0.0.1:5000

## Demo accounts

Super Admin:
- Username: superadmin
- Password: SuperAdmin123!

Admin:
- Username: admin
- Password: Admin123!

Student:
- Username: student
- Password: Student123!

## If PowerShell blocks activation

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Then:

```powershell
pip install -r requirements.txt
python seed.py
python app.py
```

## Database

The SQLite database is automatically created at:

instance/enrollment.db

You do not need MySQL or XAMPP for this project.

## Important production notes

Before deploying publicly:
- Change SECRET_KEY.
- Change all demo passwords.
- Add CSRF protection.
- Use HTTPS.
- Add stronger validation and audit logging.
- Consider Flask-Migrate/SQLAlchemy for a larger production system.
