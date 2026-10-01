import os
import sqlite3
from flask import current_app


def get_db():
    db_path = current_app.config["DATABASE"]

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    db = get_db()

    schema_path = os.path.join(
        current_app.root_path,
        "database",
        "schema.sql"
    )

    with open(schema_path, "r", encoding="utf-8") as file:
        db.executescript(file.read())

    db.commit()
    db.close()