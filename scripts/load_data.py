import os
import pandas as pd
from sqlalchemy import create_engine

# Project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_DIR = os.path.join(BASE_DIR, "database")

os.makedirs(DB_DIR, exist_ok=True)

db_path = os.path.join(DB_DIR, "bluestock_mf.db")

engine = create_engine(f"sqlite:///{db_path}")

print("Database:", db_path)

# Load dim_fund
fund_df = pd.read_csv(os.path.join(RAW_DIR, "fund_master.csv"))
fund_df.to_sql("dim_fund", engine, if_exists="replace", index=False)

# Load fact_nav
nav_df = pd.read_csv(os.path.join(PROCESSED_DIR, "nav_history_clean.csv"))
nav_df.to_sql("fact_nav", engine, if_exists="replace", index=False)

# Load fact_transactions
txn_df = pd.read_csv(os.path.join(PROCESSED_DIR, "investor_transactions_clean.csv"))
txn_df.to_sql("fact_transactions", engine, if_exists="replace", index=False)

# Load fact_performance
perf_df = pd.read_csv(os.path.join(PROCESSED_DIR, "scheme_performance_clean.csv"))
perf_df.to_sql("fact_performance", engine, if_exists="replace", index=False)

# Load fact_aum
aum_df = pd.read_csv(os.path.join(RAW_DIR, "aum_history.csv"))
aum_df.to_sql("fact_aum", engine, if_exists="replace", index=False)

print("✅ All data loaded successfully!")