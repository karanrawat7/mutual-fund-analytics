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

# Load investor_master
investor_df = pd.read_csv(os.path.join(PROCESSED_DIR, "investor_master_clean.csv"))
investor_df.to_sql("investor_master", engine, if_exists="replace", index=False)

# Load synthetic datasets
pd.read_csv(os.path.join(RAW_DIR, "synthetic_schemes.csv")).to_sql("dim_fund_synthetic", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_nav_history.csv")).to_sql("fact_nav_synthetic", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_aum_growth.csv")).to_sql("fact_aum_synthetic", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_sip_inflow.csv")).to_sql("fact_sip_inflow", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_investors.csv")).to_sql("dim_investor_synthetic", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "portfolio_holdings.csv")).to_sql("fact_holdings", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_benchmarks.csv")).to_sql("fact_benchmarks", engine, if_exists="replace", index=False)
pd.read_csv(os.path.join(RAW_DIR, "synthetic_folio_growth.csv")).to_sql("fact_folio_growth", engine, if_exists="replace", index=False)

# Load computed metrics
pd.read_csv(os.path.join(PROCESSED_DIR, "fund_metrics.csv")).to_sql("fact_metrics", engine, if_exists="replace", index=False)

print("[OK] All data loaded successfully!")