import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

df = pd.read_csv("data/raw/scheme_performance.csv")

# Convert returns to numeric

cols = [
    "one_year_return",
    "three_year_return",
    "five_year_return"
]

for col in cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Expense ratio validation

df = df[
    (df["expense_ratio"] >= 0.1)
    &
    (df["expense_ratio"] <= 2.5)
]

df.to_csv(
    "data/processed/scheme_performance_clean.csv",
    index=False
)

print("scheme_performance cleaned successfully!")