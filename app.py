from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib
import os
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Secret key for sessions
app.secret_key = os.urandom(24)

# MySQL configuration
import os
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')



# Initialize MySQL
mysql = MySQL(app)


# Helper: Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggedin" not in session:
            flash("Please login to access this page", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Home route
@app.route("/")
def home():
    if "loggedin" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_hash = hash_password(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash),
        )
        user = cursor.fetchone()

        if user:
            session["loggedin"] = True
            session["id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            msg = "Incorrect username/password!"

    return render_template("login.html", msg=msg)


# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        password_hash = hash_password(password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (username, email),
        )
        account = cursor.fetchone()

        if account:
            msg = "Account already exists!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only characters and numbers!"
        elif not username or not password or not email:
            msg = "Please fill out the form!"
        else:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for("login"))

    return render_template("signup.html", msg=msg)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


# Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
    account = cursor.fetchone()

    # Get the count of currencies
    cursor.execute("SELECT COUNT(*) as count FROM currencies")
    currency_count = cursor.fetchone()["count"]

    # Get trending currencies with increased rates
    try:
        cursor.execute(
            """
            SELECT 
                base_currency, 
                target_currency, 
                old_rate, 
                new_rate, 
                timestamp 
            FROM 
                increased_rates
            ORDER BY 
                ((new_rate - old_rate) / old_rate * 100) DESC
            LIMIT 5
            """
        )
        increased_rates = cursor.fetchall()

        # Get trending currencies with decreased rates
        cursor.execute(
            """
            SELECT 
                base_currency, 
                target_currency, 
                old_rate, 
                new_rate, 
                timestamp 
            FROM 
                decreased_rates
            ORDER BY 
                ((new_rate - old_rate) / old_rate * 100) ASC
            LIMIT 5
            """
        )
        decreased_rates = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching trending currencies: {e}")
        increased_rates = []
        decreased_rates = []

    # General stats for the dashboard
    stats = {
        "total_currencies": currency_count,
        "total_conversions": 248,
        "monthly_trend": "+2.45%",
    }

    return render_template(
        "dashboard.html",
        account=account,
        stats=stats,
        increased_rates=increased_rates,
        decreased_rates=decreased_rates,
    )


# Add a new route to get currencies
@app.route("/get_currencies")
@login_required
def get_currencies():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT currency_code, currency_name FROM currencies ORDER BY currency_code"
    )
    currencies = cursor.fetchall()
    return jsonify({"success": True, "currencies": currencies})


# Add a route to get conversion history
@app.route("/get_conversions")
@login_required
def get_conversions():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            """
            SELECT 
                DATE_FORMAT(conversion_date, '%Y-%m-%d %H:%i') as conversion_date,
                from_currency,
                to_currency,
                amount,
                converted_amount,
                rate_used
            FROM conversion_history
            WHERE user_id = %s
            ORDER BY conversion_date DESC
            LIMIT 50
        """,
            (session["id"],),
        )

        conversions = cursor.fetchall()
        return jsonify({"success": True, "conversions": conversions})

    except Exception as e:
        print(f"Error fetching conversions: {e}")
        return jsonify({"success": False, "message": str(e)})


# Add a route to get trend data
@app.route("/get_trend_data")
@login_required
def get_trend_data():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Get the last 30 days of data for some major currencies against USD
        cursor.execute(
            """
            SELECT base_currency, target_currency, exchange_rate, DATE(timestamp) as date
            FROM trend_analysis
            WHERE base_currency = 'USD' AND target_currency IN ('EUR', 'GBP', 'JPY', 'CAD', 'AUD')
            AND timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY target_currency, timestamp ASC
        """
        )

        trend_data = cursor.fetchall()

        if not trend_data:
            return jsonify({"success": False, "message": "No trend data available"})

        # Process the data for Chart.js
        dates = []
        datasets = {}

        for record in trend_data:
            date_str = record["date"].strftime("%Y-%m-%d")
            if date_str not in dates:
                dates.append(date_str)

            currency = record["target_currency"]
            if currency not in datasets:
                datasets[currency] = {
                    "label": f"{currency}/USD",
                    "data": [],
                    "borderColor": get_color_for_currency(currency),
                    "fill": False,
                    "tension": 0.1,
                }

            datasets[currency]["data"].append(record["exchange_rate"])

        # Convert datasets dict to list for Chart.js
        datasets_list = list(datasets.values())

        return jsonify({"success": True, "labels": dates, "datasets": datasets_list})

    except Exception as e:
        print(f"Error fetching trend data: {e}")
        return jsonify({"success": False, "message": str(e)})


# Helper function to assign consistent colors to currencies
def get_color_for_currency(currency):
    colors = {
        "EUR": "rgb(54, 162, 235)",
        "GBP": "rgb(255, 99, 132)",
        "JPY": "rgb(75, 192, 192)",
        "CAD": "rgb(255, 159, 64)",
        "AUD": "rgb(153, 102, 255)",
        "CHF": "rgb(255, 205, 86)",
        "CNY": "rgb(201, 203, 207)",
        "INR": "rgb(255, 99, 71)",
    }
    return colors.get(currency, "rgb(0, 0, 0)")


# Function to update increased and decreased rates tables
@app.route("/update_rate_tables", methods=["POST"])
@login_required
def update_rate_tables():
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Clear existing data from the tables
        cursor.execute("TRUNCATE TABLE increased_rates")
        cursor.execute("TRUNCATE TABLE decreased_rates")

        # Get the latest rates and previous rates from trend_analysis
        cursor.execute(
            """
            SELECT 
                t1.base_currency, 
                t1.target_currency, 
                t2.exchange_rate AS old_rate, 
                t1.exchange_rate AS new_rate,
                t1.timestamp
            FROM 
                (SELECT * FROM trend_analysis WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 DAY)) t1
            JOIN 
                (SELECT * FROM trend_analysis WHERE timestamp < DATE_SUB(NOW(), INTERVAL 1 DAY) 
                 AND timestamp >= DATE_SUB(NOW(), INTERVAL 2 DAY)) t2
            ON 
                t1.base_currency = t2.base_currency AND t1.target_currency = t2.target_currency
            """
        )
        rates = cursor.fetchall()

        # Separate into increased and decreased rates
        for rate in rates:
            if rate["new_rate"] > rate["old_rate"]:
                cursor.execute(
                    """
                    INSERT INTO increased_rates 
                    (base_currency, target_currency, old_rate, new_rate, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        rate["base_currency"],
                        rate["target_currency"],
                        rate["old_rate"],
                        rate["new_rate"],
                        rate["timestamp"],
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO decreased_rates 
                    (base_currency, target_currency, old_rate, new_rate, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        rate["base_currency"],
                        rate["target_currency"],
                        rate["old_rate"],
                        rate["new_rate"],
                        rate["timestamp"],
                    ),
                )

        mysql.connection.commit()
        return jsonify({"success": True, "message": "Rate tables updated successfully"})

    except Exception as e:
        print(f"Error updating rate tables: {e}")
        return jsonify({"success": False, "message": str(e)})


# Exchange Rates
@app.route("/exchange_rates")
@login_required
def exchange_rates():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Fetch all exchange rates from the table
    cursor.execute("SELECT * FROM exchange_rates ORDER BY timestamp DESC")
    rates = cursor.fetchall()

    # Process datetime objects if needed
    for rate in rates:
        if isinstance(rate["timestamp"], datetime):
            # Nothing needed as we'll format in the template
            pass
        else:
            # Convert to datetime if it's not already
            rate["timestamp"] = datetime.strptime(
                str(rate["timestamp"]), "%Y-%m-%d %H:%M:%S"
            )

    return render_template("exchange_rates.html", rates=rates)


# Currency Converter Page
@app.route("/currency_converter")
@login_required
def currency_converter():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Get all currencies for both dropdown menus
    cursor.execute("SELECT currency_code FROM currencies ORDER BY currency_code")
    currencies = cursor.fetchall()

    # Convert to a simple list of currency codes
    currency_codes = [currency["currency_code"] for currency in currencies]

    return render_template("currency_converter.html", currencies=currency_codes)


# Conversion Logic
@app.route("/convert", methods=["POST"])
@login_required
def convert():
    try:
        # Get and validate input values
        amount = float(request.form["amount"])
        from_currency = request.form["from_currency"]
        to_currency = request.form["to_currency"]

        # Validate amount
        if amount <= 0:
            return jsonify(
                {"success": False, "message": "Amount must be greater than 0"}
            )

        # Check if currencies are the same
        if from_currency == to_currency:
            return jsonify({"success": True, "converted_amount": amount})

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Try direct conversion first
        cursor.execute(
            """
            SELECT exchange_rate 
            FROM exchange_rates 
            WHERE base_currency = %s AND target_currency = %s 
            ORDER BY timestamp DESC LIMIT 1
            """,
            (from_currency, to_currency),
        )
        result = cursor.fetchone()

        if result:
            exchange_rate = float(result["exchange_rate"])
        else:
            # Try inverse rate if direct rate not found
            cursor.execute(
                """
                SELECT exchange_rate 
                FROM exchange_rates 
                WHERE base_currency = %s AND target_currency = %s 
                ORDER BY timestamp DESC LIMIT 1
                """,
                (to_currency, from_currency),
            )
            inverse_result = cursor.fetchone()

            if inverse_result:
                exchange_rate = 1 / float(inverse_result["exchange_rate"])
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": f"Exchange rate not found for {from_currency} to {to_currency}",
                    }
                )

        # Calculate converted amount with proper rounding
        converted_amount = round(amount * exchange_rate, 2)

        # Log the conversion
        try:
            cursor.execute(
                """
                INSERT INTO conversion_history 
                (user_id, from_currency, to_currency, amount, converted_amount, rate_used, conversion_date)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    session["id"],
                    from_currency,
                    to_currency,
                    amount,
                    converted_amount,
                    exchange_rate,
                ),
            )
            mysql.connection.commit()
        except Exception as e:
            print(f"Error logging conversion: {e}")
            # Continue even if logging fails
            pass

        return jsonify(
            {
                "success": True,
                "converted_amount": converted_amount,
                "rate_used": exchange_rate,
            }
        )

    except ValueError as e:
        return jsonify(
            {
                "success": False,
                "message": "Invalid amount format. Please enter a valid number.",
            }
        )
    except Exception as e:
        print(f"Conversion error: {e}")
        return jsonify(
            {
                "success": False,
                "message": "An error occurred during conversion. Please try again.",
            }
        )


# User Profile
@app.route("/profile")
@login_required
def profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
    account = cursor.fetchone()
    return render_template("profile.html", account=account)


# Edit Profile
@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]

        cursor.execute(
            "SELECT * FROM users WHERE (username = %s OR email = %s) AND id != %s",
            (new_username, new_email, session["id"]),
        )
        existing = cursor.fetchone()

        if existing:
            flash("Username or email already in use.", "danger")
            return redirect(url_for("edit_profile"))

        cursor.execute(
            "UPDATE users SET username = %s, email = %s WHERE id = %s",
            (new_username, new_email, session["id"]),
        )
        mysql.connection.commit()
        session["username"] = new_username
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    cursor.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
    account = cursor.fetchone()
    return render_template("edit_profile.html", account=account)


# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=3000)



