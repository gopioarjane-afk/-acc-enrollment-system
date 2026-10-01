import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "acc-enrollment-system-secret-key"
    )

    DATABASE = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "instance",
        "enrollment.db"
    )