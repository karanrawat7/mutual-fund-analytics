import pandas as pd
import numpy as np
from scipy import stats
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

print("Starting quantitative calculations...")

# Load datasets
df_schemes = pd.read_csv(os.path.join(RAW_DIR, "synthetic_schemes.csv"))
df_nav = pd.read_csv(os.path.join(RAW_DIR, "synthetic_nav_history.csv"))
df_benchmarks = pd.read_csv(os.path.join(RAW_DIR, "synthetic_benchmarks.csv"))

# Parse dates
df_nav["date"] = pd.to_datetime(df_nav["date"])
df_benchmarks["date"] = pd.to_datetime(df_benchmarks["date"])

# Ensure sorting
df_nav = df_nav.sort_values(["amfi_code", "date"])
df_benchmarks = df_benchmarks.sort_values("date")

# Compute daily returns for benchmarks
df_benchmarks["nifty50_return"] = df_benchmarks["nifty_50"].pct_change()
df_benchmarks["nifty100_return"] = df_benchmarks["nifty_100"].pct_change()
df_benchmarks = df_benchmarks.dropna().copy()

# Date constants
END_DATE = pd.to_datetime("2026-06-30")
ONE_YEAR_AGO = pd.to_datetime("2025-06-30")
THREE_YEARS_AGO = pd.to_datetime("2023-06-30")
FIVE_YEARS_AGO = pd.to_datetime("2021-06-30")

rf_annual = 0.065  # 6.5% Risk Free Rate
rf_daily = rf_annual / 252

fund_metrics = []

for idx, s in df_schemes.iterrows():
    code = s["scheme_code"]
    name = s["scheme_name"]
    category = s["category"]
    
    # Filter NAV for this fund
    df_f = df_nav[df_nav["amfi_code"] == code].copy()
    df_f = df_f.sort_values("date")
    
    # Calculate daily returns
    df_f["daily_return"] = df_f["nav"].pct_change()
    
    # Merge with benchmark returns to align dates
    df_merged = pd.merge(df_f, df_benchmarks[["date", "nifty50_return", "nifty100_return"]], on="date", how="inner")
    df_merged = df_merged.dropna().copy()
    
    # CAGR calculations
    nav_end = df_f[df_f["date"] <= END_DATE]["nav"].values[-1]
    
    # 1 Year
    df_1y = df_f[(df_f["date"] >= ONE_YEAR_AGO) & (df_f["date"] <= END_DATE)]
    nav_start_1y = df_1y["nav"].values[0] if len(df_1y) > 0 else df_f["nav"].values[0]
    cagr_1y = (nav_end / nav_start_1y) ** (1/1.0) - 1
    
    # 3 Year
    df_3y = df_f[(df_f["date"] >= THREE_YEARS_AGO) & (df_f["date"] <= END_DATE)]
    nav_start_3y = df_3y["nav"].values[0] if len(df_3y) > 0 else df_f["nav"].values[0]
    cagr_3y = (nav_end / nav_start_3y) ** (1/3.0) - 1
    
    # 5 Year
    df_5y = df_f[(df_f["date"] >= FIVE_YEARS_AGO) & (df_f["date"] <= END_DATE)]
    nav_start_5y = df_5y["nav"].values[0] if len(df_5y) > 0 else df_f["nav"].values[0]
    cagr_5y = (nav_end / nav_start_5y) ** (1/5.0) - 1
    
    # Sharpe & Sortino (using all returns in the dataset)
    returns = df_merged["daily_return"].values
    mean_ret = np.mean(returns)
    std_ret = np.std(returns) if len(returns) > 1 else 0.0001
    
    sharpe = ((mean_ret - rf_daily) / std_ret) * np.sqrt(252) if std_ret > 0 else 0
    
    downside_returns = returns[returns < 0]
    std_downside = np.std(downside_returns) if len(downside_returns) > 1 else 0.0001
    sortino = ((mean_ret - rf_daily) / std_downside) * np.sqrt(252) if std_downside > 0 else 0
    
    # Alpha & Beta vs Nifty 100
    nifty100_ret = df_merged["nifty100_return"].values
    beta, alpha_daily, r_value, p_value, std_err = stats.linregress(nifty100_ret, returns)
    alpha = alpha_daily * 252
    
    # Max Drawdown
    navs = df_f["nav"].values
    running_max = np.maximum.accumulate(navs)
    drawdowns = (navs / running_max) - 1
    max_dd = np.min(drawdowns)
    
    # Find Max Drawdown dates
    worst_idx = np.argmin(drawdowns)
    worst_date = df_f["date"].values[worst_idx]
    
    # Backtrack to find peak date
    peak_idx = np.argmax(navs[:worst_idx+1])
    peak_date = df_f["date"].values[peak_idx]
    
    # Convert dates to string format
    worst_date_str = pd.to_datetime(worst_date).strftime("%Y-%m-%d")
    peak_date_str = pd.to_datetime(peak_date).strftime("%Y-%m-%d")
    
    # Tracking Error vs Nifty 50 and Nifty 100 (Over 3 years)
    df_te = df_merged[df_merged["date"] >= THREE_YEARS_AGO]
    te_50 = np.std(df_te["daily_return"].values - df_te["nifty50_return"].values) * np.sqrt(252)
    te_100 = np.std(df_te["daily_return"].values - df_te["nifty100_return"].values) * np.sqrt(252)
    
    fund_metrics.append({
        "scheme_code": code,
        "scheme_name": name,
        "category": category,
        "expense_ratio": s["expense_ratio"],
        "cagr_1y": round(cagr_1y * 100, 2),
        "cagr_3y": round(cagr_3y * 100, 2),
        "cagr_5y": round(cagr_5y * 100, 2),
        "sharpe_ratio": round(sharpe, 4),
        "sortino_ratio": round(sortino, 4),
        "alpha": round(alpha * 100, 2),  # In % terms
        "beta": round(beta, 4),
        "max_drawdown": round(max_dd * 100, 2),
        "drawdown_start": peak_date_str,
        "drawdown_end": worst_date_str,
        "tracking_error_nifty50": round(te_50 * 100, 2),
        "tracking_error_nifty100": round(te_100 * 100, 2)
    })

df_metrics = pd.DataFrame(fund_metrics)

# ----------------------------------------------------
# 8. Compute Scorecard
# ----------------------------------------------------
# 30% x 3yr return rank + 25% x Sharpe rank + 20% x Alpha rank + 15% x expense ratio rank (inverse) + 10% x max DD rank (inverse)
# Calculate percentile ranks (0 to 100)
df_metrics["rank_return"] = df_metrics["cagr_3y"].rank(pct=True) * 100
df_metrics["rank_sharpe"] = df_metrics["sharpe_ratio"].rank(pct=True) * 100
df_metrics["rank_alpha"] = df_metrics["alpha"].rank(pct=True) * 100
df_metrics["rank_expense"] = df_metrics["expense_ratio"].rank(ascending=False, pct=True) * 100
df_metrics["rank_drawdown"] = df_metrics["max_drawdown"].rank(ascending=False, pct=True) * 100  # less negative = rank is higher

# Weighted Scorecard
df_metrics["scorecard"] = (
    0.30 * df_metrics["rank_return"] +
    0.25 * df_metrics["rank_sharpe"] +
    0.20 * df_metrics["rank_alpha"] +
    0.15 * df_metrics["rank_expense"] +
    0.10 * df_metrics["rank_drawdown"]
)

df_metrics["scorecard"] = df_metrics["scorecard"].round(2)

# Drop rank working columns
df_metrics = df_metrics.drop(columns=["rank_return", "rank_sharpe", "rank_alpha", "rank_expense", "rank_drawdown"])

df_metrics.to_csv(os.path.join(PROCESSED_DIR, "fund_metrics.csv"), index=False)
print("Completed calculations. Saved metrics to fund_metrics.csv")
