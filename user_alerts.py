from datetime import datetime

# In-memory exchange rates (example data)
exchange_rates = [
    {"base_currency": "USD", "target_currency": "EUR", "exchange_rate": 0.92},
    {"base_currency": "USD", "target_currency": "JPY", "exchange_rate": 150},
    {"base_currency": "EUR", "target_currency": "GBP", "exchange_rate": 0.88},
]

# In-memory user alerts (example data)
user_alerts = [
    {"user_id": 1, "base_currency": "USD", "target_currency": "EUR", "threshold_rate": 0.91, "alert_status": "Pending"},
    {"user_id": 2, "base_currency": "USD", "target_currency": "JPY", "threshold_rate": 155, "alert_status": "Pending"},
    {"user_id": 3, "base_currency": "EUR", "target_currency": "GBP", "threshold_rate": 0.85, "alert_status": "Pending"},
]

def check_alerts():
    """Check exchange rates against user alerts and update status in-memory."""
    triggered_count = 0
    for alert in user_alerts:
        for rate in exchange_rates:
            if (alert["base_currency"] == rate["base_currency"] and
                alert["target_currency"] == rate["target_currency"] and
                rate["exchange_rate"] >= alert["threshold_rate"] and
                alert["alert_status"] == "Pending"):
                alert["alert_status"] = "Triggered"
                triggered_count += 1
                print(f"🚨 Alert triggered for user {alert['user_id']}: "
                      f"{alert['base_currency']} -> {alert['target_currency']} @ {rate['exchange_rate']}")

    print(f"✅ Checked alerts. Total triggered: {triggered_count}")

if __name__ == "__main__":
    check_alerts()
