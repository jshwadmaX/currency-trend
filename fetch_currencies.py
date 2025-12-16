import requests

# API Key & URL
api_key = "0747d93d32f8e90f1d01f1d6"
api_url = f"https://v6.exchangerate-api.com/v6/{api_key}/codes"

try:
    # Fetch currency data from API
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an error for HTTP failures
    data = response.json()

    # Extract currency codes and names
    if "supported_codes" not in data:
        print("Error: 'supported_codes' not found in API response.")
    else:
        currencies = data["supported_codes"]
        # currencies is a list of [code, name] pairs
        print(f"Fetched {len(currencies)} currencies from API:")
        for code, name in currencies:
            print(f"{code}: {name}")

except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
