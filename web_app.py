from pathlib import Path
import sqlite3
from datetime import date
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "finance.db"

app = Flask(__name__)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        """)

ensure_database()

def fetch_transactions():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, transaction_date, transaction_type, category, amount, description
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """).fetchall()
    return [dict(row) for row in rows]

@app.route("/")
def index():
    return render_template("index.html", today=date.today().isoformat())

@app.get("/api/transactions")
def api_transactions():
    rows = fetch_transactions()
    income = sum(float(r["amount"]) for r in rows if r["transaction_type"] == "Income")
    expenses = sum(float(r["amount"]) for r in rows if r["transaction_type"] == "Expense")
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    return jsonify({
        "transactions": rows,
        "summary": {
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "savings_rate": savings_rate,
            "count": len(rows)
        }
    })

@app.post("/api/transactions")
def add_transaction():
    data = request.get_json(silent=True) or {}
    transaction_type = data.get("transaction_type")
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    transaction_date = str(data.get("transaction_date", "")).strip()
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a valid amount."}), 400

    if transaction_type not in ("Income", "Expense"):
        return jsonify({"error": "Choose Income or Expense."}), 400
    if not category:
        return jsonify({"error": "Choose a category."}), 400
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than zero."}), 400
    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        return jsonify({"error": "Choose a valid date."}), 400

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions
                (transaction_date, transaction_type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (transaction_date, transaction_type, category, amount, description))
    return jsonify({"message": "Transaction saved successfully."}), 201

@app.delete("/api/transactions/<int:transaction_id>")
def remove_transaction(transaction_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Transaction not found."}), 404
    return jsonify({"message": "Transaction deleted."})

@app.get("/health")
def health():
    return jsonify({"status": "ok", "database": DB_PATH.name})

if __name__ == "__main__":
    ensure_database()
    print(f"FinTrack is using database: {DB_PATH}")
    app.run(debug=True, port=5000)
