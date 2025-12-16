from datetime import datetime

# In-memory storage for transactions
transactions = []

def insert_transaction(user_id, base_currency, target_currency, amount, exchange_rate):
    """Log a new transaction in-memory"""
    exchanged_amount = round(amount * exchange_rate, 6)  # Calculate exchanged amount
    timestamp = datetime.now()

    # Create transaction record
    transaction = {
        "user_id": user_id,
        "base_currency": base_currency,
        "target_currency": target_currency,
        "amount": amount,
        "exchanged_amount": exchanged_amount,
        "exchange_rate": exchange_rate,
        "timestamp": timestamp
    }

    transactions.append(transaction)
    print(
        f"✅ Transaction added: {amount} {base_currency} → {exchanged_amount} {target_currency} @ {exchange_rate} on {timestamp}"
    )

# Simulating User Transactions
insert_transaction(5, "USD", "EUR", 100, 0.92)       # Example: User converts 100 USD to EUR
insert_transaction(6, "JPY", "USD", 10000, 0.0072)  # Example: 10,000 JPY to USD

# Optional: print all transactions
print("\nAll transactions:")
for t in transactions:
    print(t)
