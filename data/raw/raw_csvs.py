import pandas as pd
import os

# Create data/raw folder
os.makedirs("data/raw", exist_ok=True)

# 1. nav_history.csv
nav_history = pd.DataFrame({
    "amfi_code": [101, 101, 102, 102, 103],
    "date": ["2026-01-01", "2026-01-02", "2026-01-01", "2026-01-02", "2026-01-01"],
    "nav": [25.45, 25.60, 18.20, 18.35, 42.10]
})
nav_history.to_csv("data/raw/nav_history.csv", index=False)

# 2. investor_transactions.csv
transactions = pd.DataFrame({
    "transaction_id": [1, 2, 3, 4, 5],
    "investor_id": [1001, 1002, 1003, 1001, 1004],
    "amfi_code": [101, 102, 103, 101, 102],
    "transaction_type": ["SIP", "Lumpsum", "Redemption", "sip", "LUMP SUM"],
    "amount": [5000, 15000, 7000, 5000, 10000],
    "date": ["2026-01-02", "02/01/2026", "03-Jan-2026", "2026/01/04", "05-01-2026"],
    "kyc_status": ["Verified", "Pending", "Verified", "Rejected", "Verified"]
})
transactions.to_csv("data/raw/investor_transactions.csv", index=False)

# 3. scheme_performance.csv
performance = pd.DataFrame({
    "amfi_code": [101, 102, 103],
    "one_year_return": [12.5, 10.3, 15.2],
    "three_year_return": [35.8, 28.4, 42.6],
    "five_year_return": [75.4, 60.8, 88.3],
    "expense_ratio": [1.2, 0.85, 1.6]
})
performance.to_csv("data/raw/scheme_performance.csv", index=False)

# 4. fund_master.csv
fund_master = pd.DataFrame({
    "amfi_code": [101, 102, 103],
    "fund_name": ["Alpha Growth", "Balanced Wealth", "Blue Equity"],
    "category": ["Equity", "Hybrid", "Equity"],
    "fund_house": ["ABC AMC", "XYZ AMC", "Blue AMC"]
})
fund_master.to_csv("data/raw/fund_master.csv", index=False)

# 5. aum_history.csv
aum = pd.DataFrame({
    "amfi_code": [101, 102, 103],
    "date": ["2026-01-01", "2026-01-01", "2026-01-01"],
    "aum": [250000000, 180000000, 300000000]
})
aum.to_csv("data/raw/aum_history.csv", index=False)

# 6. benchmark_returns.csv
benchmark = pd.DataFrame({
    "benchmark_name": ["Nifty 50", "Sensex", "Nifty Midcap"],
    "year_return": [11.5, 10.8, 14.2]
})
benchmark.to_csv("data/raw/benchmark_returns.csv", index=False)

# 7. fund_manager.csv
manager = pd.DataFrame({
    "manager_id": [1, 2, 3],
    "manager_name": ["Amit Sharma", "Neha Singh", "Rahul Verma"],
    "amfi_code": [101, 102, 103]
})
manager.to_csv("data/raw/fund_manager.csv", index=False)

# 8. investor_master.csv
investor = pd.DataFrame({
    "investor_id": [1001, 1002, 1003, 1004],
    "investor_name": ["Rahul", "Priya", "Ankit", "Sneha"],
    "state": ["UP", "Delhi", "Maharashtra", "Karnataka"],
    "kyc_status": ["Verified", "Pending", "Verified", "Rejected"]
})
investor.to_csv("data/raw/investor_master.csv", index=False)

# 9. scheme_category.csv
category = pd.DataFrame({
    "category_id": [1, 2],
    "category_name": ["Equity", "Hybrid"]
})
category.to_csv("data/raw/scheme_category.csv", index=False)

# 10. states.csv
states = pd.DataFrame({
    "state_code": ["UP", "DL", "MH", "KA"],
    "state_name": ["Uttar Pradesh", "Delhi", "Maharashtra", "Karnataka"]
})
states.to_csv("data/raw/states.csv", index=False)

print("✅ All 10 raw CSV files created successfully in data/raw/")