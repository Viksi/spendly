import os
import sqlite3
from calendar import monthrange
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "spendly.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
    if existing > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    days_in_month = monthrange(today.year, today.month)[1]

    def day_str(day):
        day = min(day, days_in_month)
        return f"{today.year:04d}-{today.month:02d}-{day:02d}"

    expenses = [
        # (amount, category, day_of_month, description)
        (45.50, "Food", 2, "Groceries at supermarket"),
        (12.00, "Food", 15, "Lunch with coworkers"),
        (30.00, "Transport", 4, "Monthly bus pass"),
        (89.99, "Bills", 5, "Electricity bill"),
        (60.00, "Health", 9, "Pharmacy purchase"),
        (25.00, "Entertainment", 13, "Movie tickets"),
        (120.75, "Shopping", 18, "New shoes"),
        (15.25, "Other", 22, "Miscellaneous expense"),
    ]

    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        [
            (user_id, amount, category, day_str(day), description)
            for amount, category, day, description in expenses
        ],
    )
    conn.commit()
    conn.close()
