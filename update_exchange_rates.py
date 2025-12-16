import mysql.connector
import requests
import time
from datetime import datetime

# Database connection details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Replace with your MySQL username
    "password": "root123",  # Replace with your MySQL password
    "database": "currency_trend_management",
}

# API details
API_KEY = "0747d93d32f8e90f1d01f1d6"
BASE_CURRENCY = "USD"  # Change base currency if needed
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{BASE_CURRENCY}"


def fetch_exchange_rates():
    """Fetch live exchange rates from the API."""
    try:
        response = requests.get(API_URL)
        data = response.json()

        if data.get("result") != "success":
            print("❌ Error fetching exchange rates:", data)
            return None
        return data["conversion_rates"]

    except requests.exceptions.RequestException as e:
        print("❌ API Request Error:", e)
        return None


def update_database(rates):
    """Update the exchange_rates table with new data."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Ensure currencies exist in the table
        for currency_code in rates.keys():
            cursor.execute(
                "INSERT IGNORE INTO currencies (currency_code, currency_name) VALUES (%s, %s)",
                (currency_code, currency_code),
            )

        # Update exchange rates
        for target_currency, rate in rates.items():
            cursor.execute(
                """
                INSERT INTO exchange_rates (base_currency, target_currency, exchange_rate, timestamp)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE exchange_rate = VALUES(exchange_rate), timestamp = VALUES(timestamp)
            """,
                (BASE_CURRENCY, target_currency, rate, datetime.now()),
            )

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Exchange rates updated at {datetime.now()}")

    except mysql.connector.Error as e:
        print("❌ Database Error:", e)


def main():
    """Fetch and update exchange rates every 10 seconds for real-time updates."""
    while True:
        print("🔄 Fetching live exchange rates...")
        rates = fetch_exchange_rates()
        if rates:
            update_database(rates)
        print("⏳ Waiting for 10 seconds before next update...\n")
        time.sleep(10)  # Update every 10 seconds


if __name__ == "__main__":
    main()
