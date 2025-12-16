from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import re
import hashlib
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage
users = {}  # username -> user dict
currencies = [
    {"currency_code": "USD", "currency_name": "US Dollar"},
    {"currency_code": "EUR", "currency_name": "Euro"},
    {"currency_code": "JPY", "currency_name": "Japanese Yen"},
    {"currency_code": "GBP", "currency_name": "British Pound"},
]
conversion_history = []
next_user_id = 1

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggedin" not in session:
            flash("Please login to access this page", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route("/")
def home():
    return redirect(url_for("dashboard")) if "loggedin" in session else redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global next_user_id
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        password_hash = hash_password(password)

        if username in users or any(u['email'] == email for u in users.values()):
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers!"
        elif not username or not password or not email:
            msg = "Please fill out the form!"
        else:
            users[username] = {"id": next_user_id, "username": username, "email": email, "password_hash": password_hash}
            next_user_id += 1
            flash("Successfully registered!", "success")
            return redirect(url_for("login"))

    return render_template("signup.html", msg=msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = hash_password(password)
        user = users.get(username)
        if user and user["password_hash"] == password_hash:
            session["loggedin"] = True
            session["id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            msg = "Incorrect username/password!"
    return render_template("login.html", msg=msg)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out!", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    account = users.get(session["username"])
    stats = {
        "total_currencies": len(currencies),
        "total_conversions": len(conversion_history),
        "monthly_trend": "+2.45%",
    }
    return render_template("dashboard.html", account=account, stats=stats)
    
@app.route("/profile")
@login_required
def profile():
    account = users.get(session["username"])
    return render_template("profile.html", account=account)

@app.route("/exchange_rates")
@login_required
def exchange_rates():
    account = users.get(session["username"])
    # Sample exchange rates
    rates = [
        {"base_currency": "USD", "target_currency": "EUR", "exchange_rate": 0.9, "timestamp": datetime.now()},
        {"base_currency": "USD", "target_currency": "JPY", "exchange_rate": 150, "timestamp": datetime.now()},
        {"base_currency": "USD", "target_currency": "GBP", "exchange_rate": 0.8, "timestamp": datetime.now()},
    ]
    return render_template("exchange_rates.html", account=account, rates=rates)

@app.route("/currency_converter")
@login_required
def currency_converter():
    account = users.get(session["username"])
    return render_template("currency_converter.html", account=account, currencies=currencies)

@app.route("/get_currencies")
@login_required
def get_currencies():
    return jsonify({"success": True, "currencies": currencies})

@app.route("/convert", methods=["POST"])
@login_required
def convert():
    try:
        amount = float(request.form["amount"])
        from_currency = request.form["from_currency"]
        to_currency = request.form["to_currency"]

        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be > 0"})

        rates = {
            "USD": {"EUR": 0.9, "JPY": 150, "GBP": 0.8},
            "EUR": {"USD": 1.1, "JPY": 166, "GBP": 0.88},
            "JPY": {"USD": 0.0067, "EUR": 0.006, "GBP": 0.0053},
            "GBP": {"USD": 1.25, "EUR": 1.14, "JPY": 188},
        }

        if from_currency == to_currency:
            converted_amount = amount
            rate_used = 1
        else:
            rate_used = rates.get(from_currency, {}).get(to_currency)
            if not rate_used:
                return jsonify({"success": False, "message": "Exchange rate not found."})
            converted_amount = round(amount * rate_used, 2)

        conversion_history.append({
            "user_id": session["id"],
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "converted_amount": converted_amount,
            "rate_used": rate_used,
            "conversion_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return jsonify({"success": True, "converted_amount": converted_amount, "rate_used": rate_used})

    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount format."})

@app.route("/get_conversions")
@login_required
def get_conversions():
    user_conversions = [c for c in conversion_history if c["user_id"] == session["id"]]
    return jsonify({"success": True, "conversions": user_conversions})

if __name__ == "__main__":
    app.run(debug=True, port=3000)
