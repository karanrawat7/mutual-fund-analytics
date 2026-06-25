import pandas as pd
import os

# Create processed folder
os.makedirs("data/processed", exist_ok=True)

# Read CSV
df = pd.read_csv("data/raw/nav_history.csv")

# Convert date
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Sort
df = df.sort_values(["amfi_code", "date"])

# Remove duplicates
df = df.drop_duplicates()

# Forward fill NAV
df["nav"] = df.groupby("amfi_code")["nav"].ffill()

# Keep only positive NAV
df = df[df["nav"] > 0]

# Save cleaned file
df.to_csv("data/processed/nav_history_clean.csv", index=False)

print("nav_history cleaned successfully!")