import sqlite3

DB_NAME = "expenses.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    # Main expenses table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
    """)

        # NEW: Monthly budget table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            amount REAL NOT NULL
        )
    """)


    conn.commit()
    conn.close()



def add_expense_db(date, category, amount, note):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
                (date, category, amount, note))

    conn.commit()
    conn.close()


def get_all_expenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date, category, amount, note FROM expenses")
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "date": r[1], "category": r[2], "amount": float(r[3]), "note": r[4]}
        for r in rows
    ]


def filter_by_date_range(start_date, end_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, date, category, amount, note
        FROM expenses
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (start_date, end_date))
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "date": r[1], "category": r[2], "amount": float(r[3]), "note": r[4]}
        for r in rows
    ]


def delete_expense_db(expense_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    conn.commit()
    conn.close()


def update_expense_db(expense_id, date, category, amount, note):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE expenses
        SET date = ?, category = ?, amount = ?, note = ?
        WHERE id = ?
    """, (date, category, amount, note, expense_id))

    conn.commit()
    conn.close()

def add_category_db(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def update_category_db(category_id, new_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id))
    conn.commit()
    conn.close()

def set_budget_db(category, amount):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO budgets (category, amount)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET amount = excluded.amount
    """, (category, amount))
    conn.commit()
    conn.close()

def get_budgets_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, amount FROM budgets")
    rows = cur.fetchall()
    conn.close()
    return [{"category": r[0], "amount": float(r[1])} for r in rows]

def get_budget_for_category(category):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM budgets WHERE category = ?", (category,))
    row = cur.fetchone()
    conn.close()
    return float(row[0]) if row else None
