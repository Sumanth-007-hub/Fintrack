import os
from datetime import date
from functools import wraps

import psycopg
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg.connect(DATABASE_URL)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in."}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", today=date.today().isoformat())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        return "All fields are required.", 400

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = %s", (email,)
        ).fetchone()

        if existing:
            return "Email already registered.", 400

        user = conn.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (name, email, generate_password_hash(password))).fetchone()

    session["user_id"] = user[0]
    session["user_name"] = name

    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    with get_connection() as conn:
        user = conn.execute("""
            SELECT id, name, password_hash
            FROM users WHERE email = %s
        """, (email,)).fetchone()

    if not user or not check_password_hash(user[2], password):
        return "Invalid email or password.", 401

    session["user_id"] = user[0]
    session["user_name"] = user[1]

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/api/transactions")
@login_required
def api_transactions():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, transaction_date, transaction_type,
                   category, amount, description
            FROM transactions
            WHERE user_id = %s
            ORDER BY transaction_date DESC, id DESC
        """, (session["user_id"],)).fetchall()

    transactions = [
        {
            "id": r[0],
            "transaction_date": r[1].isoformat(),
            "transaction_type": r[2],
            "category": r[3],
            "amount": float(r[4]),
            "description": r[5]
        }
        for r in rows
    ]

    income = sum(t["amount"] for t in transactions if t["transaction_type"] == "Income")
    expenses = sum(t["amount"] for t in transactions if t["transaction_type"] == "Expense")
    savings = income - expenses

    return jsonify({
        "transactions": transactions,
        "summary": {
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "savings_rate": (savings / income * 100) if income else 0,
            "count": len(transactions)
        }
    })


@app.post("/api/transactions")
@login_required
def add_transaction():
    data = request.get_json(silent=True) or {}

    transaction_type = data.get("transaction_type")
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    transaction_date = str(data.get("transaction_date", "")).strip()

    try:
        amount = float(data.get("amount", 0))
        if not (0 < amount < float("inf")):
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a valid amount."}), 400

    if transaction_type not in ("Income", "Expense"):
        return jsonify({"error": "Choose Income or Expense."}), 400

    if not category:
        return jsonify({"error": "Choose a category."}), 400

    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        return jsonify({"error": "Choose a valid date."}), 400

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions
            (user_id, transaction_date, transaction_type,
             category, amount, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"], transaction_date,
            transaction_type, category, amount, description
        ))

    return jsonify({"message": "Transaction saved successfully."}), 201


@app.delete("/api/transactions/<int:transaction_id>")
@login_required
def remove_transaction(transaction_id):
    with get_connection() as conn:
        cursor = conn.execute("""
            DELETE FROM transactions
            WHERE id = %s AND user_id = %s
        """, (transaction_id, session["user_id"]))

        if cursor.rowcount == 0:
            return jsonify({"error": "Transaction not found."}), 404

    return jsonify({"message": "Transaction deleted."})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "database": "PostgreSQL"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
