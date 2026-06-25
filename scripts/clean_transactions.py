import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv("data/raw/investor_transactions.csv")

# Date
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Standardize transaction type
df["transaction_type"] = (
    df["transaction_type"]
    .str.strip()
    .str.lower()
)

mapping = {
    "sip": "SIP",
    "lumpsum": "Lumpsum",
    "lump sum": "Lumpsum",
    "redemption": "Redemption"
}

df["transaction_type"] = df["transaction_type"].replace(mapping)

# Amount validation
df = df[df["amount"] > 0]

# KYC validation
valid = ["Verified", "Pending", "Rejected"]

df = df[df["kyc_status"].isin(valid)]

df.to_csv(
    "data/processed/investor_transactions_clean.csv",
    index=False
)

print("investor_transactions cleaned successfully!")