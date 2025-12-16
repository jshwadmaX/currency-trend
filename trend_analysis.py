from datetime import datetime

# In-memory storage
exchange_rates = [
    {"base_currency": "USD", "target_currency": "EUR", "exchange_rate": 0.92, "timestamp": datetime.now()},
    {"base_currency": "USD", "target_currency": "JPY", "exchange_rate": 150, "timestamp": datetime.now()},
    {"base_currency": "EUR", "target_currency": "GBP", "exchange_rate": 0.88, "timestamp": datetime.now()},
]

trend_analysis = []

def update_trend_analysis():
    """Copy exchange_rates into trend_analysis in-memory"""
    for rate in exchange_rates:
        trend_analysis.append(rate.copy())
    
    print(f"✅ Trend analysis table updated with {len(trend_analysis)} records.")

if __name__ == "__main__":
    update_trend_analysis()
    # Optional: print trend_analysis
    for t in trend_analysis:
        print(t)
