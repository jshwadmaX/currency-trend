import requests
import time
from datetime import datetime

# API details
API_KEY = "0747d93d32f8e90f1d01f1d6"
BASE_CURRENCY = "USD"  # Change base currency if needed
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{BASE_CURRENCY}"

# In-memory storage for exchange rates
exchange_rates_history = []

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

def update_in_memory(rates):
    """Store exchange rates in-memory and log them."""
    timestamp = datetime.now()
    record = {"base_currency": BASE_CURRENCY, "timestamp": timestamp, "rates": rates}
    exchange_rates_history.append(record)

    print(f"✅ Exchange rates updated at {timestamp}")
    for target_currency, rate in rates.items():
        print(f"{BASE_CURRENCY} -> {target_currency}: {rate}")

def main():
    """Fetch and store exchange rates every 10 seconds."""
    while True:
        print("🔄 Fetching live exchange rates...")
        rates = fetch_exchange_rates()
        if rates:
            update_in_memory(rates)
        print("⏳ Waiting for 10 seconds before next update...\n")
        time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    main()
