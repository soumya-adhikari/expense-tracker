import sqlite3
import os
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')


def _get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        category TEXT,
        notes TEXT,
        payment_method TEXT,
        type TEXT DEFAULT 'out'
    )
    """
    )
    # migrate: ensure 'type' column exists (for older DBs)
    c.execute("PRAGMA table_info(expenses)")
    cols = [r[1] for r in c.fetchall()]
    if 'type' not in cols:
        try:
            c.execute("ALTER TABLE expenses ADD COLUMN type TEXT DEFAULT 'out'")
        except Exception:
            # ignore if cannot alter (very old SQLite?)
            pass
    conn.commit()
    conn.close()


def add_expense(amount, date_str, category, notes, payment_method, entry_type='out'):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO expenses (amount, date, category, notes, payment_method, type) VALUES (?, ?, ?, ?, ?, ?)",
        (amount, date_str, category, notes, payment_method, entry_type),
    )
    conn.commit()
    conn.close()


def list_expenses():
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, amount, date, category, notes, payment_method, type FROM expenses ORDER BY date DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def delete_expense(expense_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def export_csv(path):
    rows = list_expenses()
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'amount', 'date', 'category', 'notes', 'payment_method', 'type'])
        for r in rows:
            w.writerow(r)


def get_monthly_summary():
    conn = _get_conn()
    c = conn.cursor()
    # net amount per month where 'in' adds and 'out' subtracts
    c.execute(
        "SELECT substr(date,1,7) as month, SUM(CASE WHEN type='in' THEN amount WHEN type='out' THEN -amount ELSE 0 END) as total FROM expenses GROUP BY month ORDER BY month DESC"
    )
    rows = c.fetchall()
    conn.close()
    return rows


def get_total_by_payment_method(payment_method):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT SUM(CASE WHEN type='in' THEN amount WHEN type='out' THEN -amount ELSE 0 END) FROM expenses WHERE payment_method = ?",
        (payment_method,),
    )
    r = c.fetchone()
    conn.close()
    return r[0] if r and r[0] is not None else 0.0
