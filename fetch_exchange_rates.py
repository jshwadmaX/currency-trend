import requests
from datetime import datetime

# API Key & URL
API_KEY = "0747d93d32f8e90f1d01f1d6"
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

# Fetch data
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    if data.get("result") == "success":
        base_currency = data["base_code"]
        exchange_rates = data["conversion_rates"]
        timestamp = datetime.now()

        # Print the rates
        print(f"Exchange rates for {base_currency} at {timestamp}:")
        for target_currency, rate in exchange_rates.items():
            print(f"{base_currency} -> {target_currency}: {rate}")

    else:
        print("API returned an unsuccessful result.")

except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
