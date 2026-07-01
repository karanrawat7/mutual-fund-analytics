import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

print("Generating synthetic datasets...")

# ----------------------------------------------------
# 1. Generate 40 Schemes Metadata
# ----------------------------------------------------
fund_houses = [
    "SBI Mutual Fund", "HDFC Mutual Fund", "ICICI Prudential MF", 
    "Nippon India Mutual Fund", "Axis Mutual Fund", "Kotak Mutual Fund", 
    "DSP Mutual Fund", "Aditya Birla Sun Life MF", "UTI Mutual Fund", "Tata Mutual Fund"
]
categories = ["Equity", "Debt", "Hybrid"]

schemes = []
for i in range(40):
    code = 100001 + i
    fh = fund_houses[i % len(fund_houses)]
    cat = categories[i % len(categories)]
    
    if cat == "Equity":
        sub_cat = np.random.choice(["Large Cap", "Mid Cap", "Small Cap", "Sectoral"])
        risk = "Very High"
    elif cat == "Debt":
        sub_cat = np.random.choice(["Liquid Fund", "Corporate Bond", "Gilt Fund"])
        risk = "Low to Moderate"
    else:
        sub_cat = np.random.choice(["Aggressive Hybrid", "Balanced Advantage", "Multi Asset Allocation"])
        risk = "Moderately High"
        
    name = f"{fh.split(' ')[0]} {sub_cat} Fund - Direct"
    expense_ratio = round(np.random.uniform(0.15, 2.2), 2)
    
    schemes.append({
        "scheme_code": code,
        "scheme_name": name,
        "fund_house": fh,
        "category": cat,
        "sub_category": sub_cat,
        "risk_grade": risk,
        "expense_ratio": expense_ratio
    })

df_schemes = pd.DataFrame(schemes)
df_schemes.to_csv(os.path.join(RAW_DIR, "synthetic_schemes.csv"), index=False)
print("Saved synthetic_schemes.csv")

# ----------------------------------------------------
# 2. Generate Daily NAV and Benchmark Data (2022-01-01 to 2026-06-30)
# ----------------------------------------------------
dates = pd.date_range(start="2021-01-01", end="2026-06-30", freq="B")  # Business days
n_days = len(dates)

# Let's create market trends (returns)
# 2021: Strong growth (+18% return)
# 2022: Flat/volatile (-3% return)
# 2023: Bull market (+35% return)
# 2024: Correcting mid-year (-10%), recovering to end +12%
# 2025: Strong up (+25%)
# 2026: Consolidation (+6%)
market_returns = []
for date in dates:
    year = date.year
    if year == 2021:
        ret = np.random.normal(0.0007, 0.01)
    elif year == 2022:
        ret = np.random.normal(-0.0001, 0.01)
    elif year == 2023:
        ret = np.random.normal(0.0012, 0.009)
    elif year == 2024:
        # Correction in Q2 (Apr-Jun)
        if 4 <= date.month <= 6:
            ret = np.random.normal(-0.0018, 0.012)
        else:
            ret = np.random.normal(0.0009, 0.01)
    elif year == 2025:
        ret = np.random.normal(0.0009, 0.008)
    else:  # 2026
        ret = np.random.normal(0.0002, 0.008)
    market_returns.append(ret)

market_returns = np.array(market_returns)

# Generate Benchmark Index values
nifty50_nav = [17000.0]
nifty100_nav = [18000.0]

for r in market_returns:
    nifty50_nav.append(nifty50_nav[-1] * (1 + r + np.random.normal(0, 0.001)))
    nifty100_nav.append(nifty100_nav[-1] * (1 + r * 1.02 + np.random.normal(0, 0.001)))

nifty50_nav = nifty50_nav[1:]
nifty100_nav = nifty100_nav[1:]

df_benchmarks = pd.DataFrame({
    "date": dates.strftime("%Y-%m-%d"),
    "nifty_50": nifty50_nav,
    "nifty_100": nifty100_nav
})
df_benchmarks.to_csv(os.path.join(RAW_DIR, "synthetic_benchmarks.csv"), index=False)
print("Saved synthetic_benchmarks.csv")

# Generate Daily NAV for all 40 schemes
nav_records = []
for idx, s in df_schemes.iterrows():
    # Base NAV
    nav_val = 100.0
    beta = np.random.uniform(0.6, 1.4) if s["category"] == "Equity" else (np.random.uniform(0.1, 0.3) if s["category"] == "Debt" else np.random.uniform(0.4, 0.8))
    alpha = np.random.uniform(-0.0001, 0.0002)
    volatility = 0.012 if s["category"] == "Equity" else (0.002 if s["category"] == "Debt" else 0.007)
    
    for i, date in enumerate(dates):
        # Fund return modeled on market return with alpha/beta and noise
        fund_ret = alpha + beta * market_returns[i] + np.random.normal(0, volatility)
        
        # Prevent extreme negative return in a single day
        fund_ret = max(fund_ret, -0.08)
        
        nav_val = nav_val * (1 + fund_ret)
        # Standard NAV is always positive
        nav_val = max(nav_val, 5.0)
        
        nav_records.append({
            "amfi_code": s["scheme_code"],
            "date": date.strftime("%Y-%m-%d"),
            "nav": round(nav_val, 4)
        })

df_nav = pd.DataFrame(nav_records)
df_nav.to_csv(os.path.join(RAW_DIR, "synthetic_nav_history.csv"), index=False)
print("Saved synthetic_nav_history.csv")

# ----------------------------------------------------
# 3. Generate AUM Growth Data (2022-2025)
# ----------------------------------------------------
# Highlight SBI Mutual Fund dominance at ₹12.5L Cr in 2025
aum_records = []
for fh in fund_houses:
    # 2022 base AUM
    if fh == "SBI Mutual Fund":
        aum_val = 820000.0  # in Crore
        growth_rates = [1.12, 1.15, 1.18]  # Growth rates for 2023, 2024, 2025
    elif fh == "HDFC Mutual Fund":
        aum_val = 450000.0
        growth_rates = [1.10, 1.12, 1.14]
    elif fh == "ICICI Prudential MF":
        aum_val = 460000.0
        growth_rates = [1.11, 1.13, 1.15]
    else:
        aum_val = np.random.uniform(200000.0, 380000.0)
        growth_rates = [np.random.uniform(1.06, 1.12) for _ in range(3)]
        
    # Generate AUM for years 2022 to 2025
    aum_records.append({"fund_house": fh, "year": 2022, "aum_crore": round(aum_val, 2)})
    for idx, year in enumerate([2023, 2024, 2025]):
        aum_val = aum_val * growth_rates[idx]
        if fh == "SBI Mutual Fund" and year == 2025:
            aum_val = 1250000.0  # Force SBI to hit exactly 12.5L Cr in 2025
        aum_records.append({"fund_house": fh, "year": year, "aum_crore": round(aum_val, 2)})

df_aum = pd.DataFrame(aum_records)
df_aum.to_csv(os.path.join(RAW_DIR, "synthetic_aum_growth.csv"), index=False)
print("Saved synthetic_aum_growth.csv")

# ----------------------------------------------------
# 4. Generate SIP Inflow Data (Jan 2022 - Dec 2025)
# ----------------------------------------------------
# Monthly SIP inflow starting ~11300 and peaking at exactly 31002 in Dec 2025
months = pd.date_range(start="2022-01-01", end="2025-12-31", freq="MS")
n_months = len(months)

# Generate a smooth growth curve with minor noise, forced to start around 11300 and end at 31002
base_curve = np.linspace(11300.0, 31002.0, n_months)
noise = np.random.normal(0, 150, n_months)
noise[0] = 0.0
noise[-1] = 0.0
sip_inflows = base_curve + noise

# Category inflows
category_shares = {
    "Equity": 0.55,
    "Debt": 0.15,
    "Hybrid": 0.20,
    "Solution Oriented": 0.05,
    "Others": 0.05
}

inflow_records = []
for i, m in enumerate(months):
    tot_sip = sip_inflows[i]
    if i == n_months - 1:
        tot_sip = 31002.0  # Force exact value
    
    inflow_records.append({
        "month": m.strftime("%Y-%m"),
        "total_sip_inflow": round(tot_sip, 2),
        "Equity": round(tot_sip * category_shares["Equity"], 2),
        "Debt": round(tot_sip * category_shares["Debt"] + np.random.normal(0, 50), 2),
        "Hybrid": round(tot_sip * category_shares["Hybrid"] + np.random.normal(0, 50), 2),
        "Solution Oriented": round(tot_sip * category_shares["Solution Oriented"], 2),
        "Others": round(tot_sip * category_shares["Others"], 2)
    })

df_sip = pd.DataFrame(inflow_records)
df_sip.to_csv(os.path.join(RAW_DIR, "synthetic_sip_inflow.csv"), index=False)
print("Saved synthetic_sip_inflow.csv")

# ----------------------------------------------------
# 5. Generate Investor Demographics (1000 records)
# ----------------------------------------------------
investors = []
age_groups = ["18-25", "26-35", "36-45", "46-60", "60+"]
genders = ["Male", "Female", "Other"]
states = ["Maharashtra", "Delhi", "Uttar Pradesh", "Karnataka", "Tamil Nadu", "Gujarat", "West Bengal", "Haryana"]
city_tiers = ["T30", "B30"]

for idx in range(1000):
    age_grp = np.random.choice(age_groups, p=[0.15, 0.40, 0.25, 0.15, 0.05])
    gender = np.random.choice(genders, p=[0.58, 0.40, 0.02])
    state = np.random.choice(states, p=[0.25, 0.15, 0.12, 0.13, 0.10, 0.10, 0.08, 0.07])
    city_tier = np.random.choice(city_tiers, p=[0.62, 0.38])
    
    # SIP Amount distribution dependent on age group
    if age_grp == "18-25":
        sip_amt = np.random.lognormal(mean=7.5, sigma=0.5)  # Median ~1800
    elif age_grp == "26-35":
        sip_amt = np.random.lognormal(mean=8.4, sigma=0.6)  # Median ~4500
    elif age_grp == "36-45":
        sip_amt = np.random.lognormal(mean=8.8, sigma=0.6)  # Median ~6500
    elif age_grp == "46-60":
        sip_amt = np.random.lognormal(mean=8.7, sigma=0.7)  # Median ~6000
    else:
        sip_amt = np.random.lognormal(mean=8.0, sigma=0.8)  # Median ~3000
        
    sip_amt = round(max(sip_amt, 500.0) / 100.0) * 100.0  # Round to nearest 100
    sip_amt = min(sip_amt, 50000.0)  # Cap at 50,000
    
    investors.append({
        "investor_id": 100000 + idx,
        "age_group": age_grp,
        "gender": gender,
        "state": state,
        "city_tier": city_tier,
        "sip_amount": sip_amt
    })

df_investors = pd.DataFrame(investors)
df_investors.to_csv(os.path.join(RAW_DIR, "synthetic_investors.csv"), index=False)
print("Saved synthetic_investors.csv")

# ----------------------------------------------------
# 6. Generate Folio Count Growth
# ----------------------------------------------------
# Monthly folio count from 13.26 Cr (Jan 2022) to 26.12 Cr (Dec 2025)
folio_counts = np.linspace(13.26, 26.12, n_months)
df_folio = pd.DataFrame({
    "month": months.strftime("%Y-%m"),
    "folios_crore": np.round(folio_counts, 2)
})
df_folio.to_csv(os.path.join(RAW_DIR, "synthetic_folio_growth.csv"), index=False)
print("Saved synthetic_folio_growth.csv")

# ----------------------------------------------------
# 7. Generate Portfolio Holdings (for Equity funds)
# ----------------------------------------------------
sectors = ["Financial Services", "IT", "Oil & Gas", "Automobile", "Consumer Goods", "Pharma", "Metals", "Construction", "Power", "Telecom"]
holdings = []
equity_schemes = df_schemes[df_schemes["category"] == "Equity"]

for idx, s in equity_schemes.iterrows():
    # Random weights that sum to 100
    raw_weights = np.random.dirichlet(np.ones(len(sectors))) * 100.0
    for s_idx, sector in enumerate(sectors):
        holdings.append({
            "scheme_code": s["scheme_code"],
            "scheme_name": s["scheme_name"],
            "sector": sector,
            "holding_percentage": round(raw_weights[s_idx], 2)
        })
        
df_holdings = pd.DataFrame(holdings)
df_holdings.to_csv(os.path.join(RAW_DIR, "portfolio_holdings.csv"), index=False)
print("Saved portfolio_holdings.csv")

print("All synthetic datasets generated successfully.")
