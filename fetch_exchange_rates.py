import requests
import mysql.connector
from datetime import datetime

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="currency_db",
)
cursor = conn.cursor()

# API Key & URL
API_KEY = "0747d93d32f8e90f1d01f1d6"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

# Fetch data
response = requests.get(API_URL)
data = response.json()

if data["result"] == "success":
    base_currency = data["base_code"]
    exchange_rates = data["conversion_rates"]

    for target_currency, rate in exchange_rates.items():
        cursor.execute(
            """
            INSERT INTO Exchange_Rates (base_currency, target_currency, exchange_rate, timestamp)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE exchange_rate = VALUES(exchange_rate), timestamp = NOW()
        """,
            (base_currency, target_currency, rate, datetime.now()),
        )

# Commit and close connection
conn.commit()
cursor.close()
conn.close()
