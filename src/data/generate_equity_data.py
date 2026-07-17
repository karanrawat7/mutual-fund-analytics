"""
src/data/generate_equity_data.py
─────────────────────────────────
Generates a realistic synthetic dataset of 92 Indian NSE-listed companies
with 15 years (FY2010–FY2024) of annual financial data.

Outputs:
    data/raw/companies.xlsx  (sheets: companies, financials)

Run:
    python -m src.data.generate_equity_data
    -- or --
    python src/data/generate_equity_data.py
"""

from __future__ import annotations

import os
import random
import math
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# 1. COMPANY MASTER  (92 companies)
# ─────────────────────────────────────────────

COMPANIES = [
    # IT / Technology  (14)
    (1,  "TCS",              "TCS.NS",      "Technology", "IT Services",     "IT"),
    (2,  "Infosys",          "INFY.NS",     "Technology", "IT Services",     "IT"),
    (3,  "Wipro",            "WIPRO.NS",    "Technology", "IT Services",     "IT"),
    (4,  "HCL Technologies", "HCLTECH.NS",  "Technology", "IT Services",     "IT"),
    (5,  "Tech Mahindra",    "TECHM.NS",    "Technology", "IT Services",     "IT"),
    (6,  "Mphasis",          "MPHASIS.NS",  "Technology", "IT Services",     "IT"),
    (7,  "LTIMindtree",      "LTIM.NS",     "Technology", "IT Services",     "IT"),
    (8,  "Persistent Sys",   "PERSISTENT.NS","Technology","IT Products",     "IT"),
    (9,  "Coforge",          "COFORGE.NS",  "Technology", "IT Services",     "IT"),
    (10, "Hexaware",         "HEXAWARE.NS", "Technology", "IT Services",     "IT"),
    (11, "KPIT Tech",        "KPITTECH.NS", "Technology", "IT Products",     "IT"),
    (12, "Tata Elxsi",       "TATAELXSI.NS","Technology", "IT Products",     "IT"),
    (13, "Zensar Tech",      "ZENSARTECH.NS","Technology","IT Services",     "IT"),
    (14, "Mastek",           "MASTEK.NS",   "Technology", "IT Services",     "IT"),

    # Financials — Banks (8)
    (15, "HDFC Bank",        "HDFCBANK.NS", "Financials", "Private Banks",   "Banking"),
    (16, "ICICI Bank",       "ICICIBANK.NS","Financials", "Private Banks",   "Banking"),
    (17, "Axis Bank",        "AXISBANK.NS", "Financials", "Private Banks",   "Banking"),
    (18, "Kotak Mahindra",   "KOTAKBANK.NS","Financials", "Private Banks",   "Banking"),
    (19, "State Bank",       "SBIN.NS",     "Financials", "Public Banks",    "Banking"),
    (20, "Bank of Baroda",   "BANKBARODA.NS","Financials","Public Banks",    "Banking"),
    (21, "Punjab Natl Bank", "PNB.NS",      "Financials", "Public Banks",    "Banking"),
    (22, "Canara Bank",      "CANARABANK.NS","Financials","Public Banks",    "Banking"),

    # Financials — NBFC (6)
    (23, "Bajaj Finance",    "BAJFINANCE.NS","Financials","NBFC",            "NBFC"),
    (24, "Bajaj Finserv",    "BAJAJFINSV.NS","Financials","NBFC",            "NBFC"),
    (25, "Muthoot Finance",  "MUTHOOTFIN.NS","Financials","NBFC",            "NBFC"),
    (26, "Shriram Finance",  "SHRIRAMFIN.NS","Financials","NBFC",            "NBFC"),
    (27, "Cholamandalam",    "CHOLAFIN.NS", "Financials", "NBFC",            "NBFC"),
    (28, "L&T Finance",      "LTF.NS",      "Financials", "NBFC",            "NBFC"),

    # Financials — Insurance (5)
    (29, "HDFC Life",        "HDFCLIFE.NS", "Financials", "Insurance",       "Insurance"),
    (30, "SBI Life",         "SBILIFE.NS",  "Financials", "Insurance",       "Insurance"),
    (31, "ICICI Prudential", "ICICIPRULI.NS","Financials","Insurance",       "Insurance"),
    (32, "LIC Housing Fin",  "LICHSGFIN.NS","Financials", "Housing Finance", "NBFC"),
    (33, "General Ins Corp", "GICRE.NS",    "Financials", "Insurance",       "Insurance"),

    # FMCG  (10)
    (34, "Hindustan Unilever","HINDUNILVR.NS","FMCG",    "FMCG",            "FMCG"),
    (35, "ITC",               "ITC.NS",      "FMCG",    "Diversified FMCG", "FMCG"),
    (36, "Nestle India",      "NESTLEIND.NS","FMCG",    "FMCG",            "FMCG"),
    (37, "Britannia",         "BRITANNIA.NS","FMCG",    "FMCG",            "FMCG"),
    (38, "Dabur India",       "DABUR.NS",    "FMCG",    "FMCG",            "FMCG"),
    (39, "Marico",            "MARICO.NS",   "FMCG",    "FMCG",            "FMCG"),
    (40, "Godrej Consumer",   "GODREJCP.NS", "FMCG",    "FMCG",            "FMCG"),
    (41, "Colgate-Palmolive", "COLPAL.NS",   "FMCG",    "FMCG",            "FMCG"),
    (42, "Tata Consumer",     "TATACONSUM.NS","FMCG",   "FMCG",            "FMCG"),
    (43, "Emami",             "EMAMILTD.NS", "FMCG",    "FMCG",            "FMCG"),

    # Pharma  (8)
    (44, "Sun Pharma",        "SUNPHARMA.NS","Pharma",   "Pharma",          "Pharma"),
    (45, "Dr Reddys",         "DRREDDY.NS",  "Pharma",   "Pharma",          "Pharma"),
    (46, "Cipla",             "CIPLA.NS",    "Pharma",   "Pharma",          "Pharma"),
    (47, "Divi's Labs",       "DIVISLAB.NS", "Pharma",   "Pharma APIs",     "Pharma"),
    (48, "Aurobindo Pharma",  "AUROPHARMA.NS","Pharma",  "Pharma",          "Pharma"),
    (49, "Lupin",             "LUPIN.NS",    "Pharma",   "Pharma",          "Pharma"),
    (50, "Torrent Pharma",    "TORNTPHARM.NS","Pharma",  "Pharma",          "Pharma"),
    (51, "Ipca Labs",         "IPCALAB.NS",  "Pharma",   "Pharma",          "Pharma"),

    # Automobile  (8)
    (52, "Tata Motors",       "TATAMOTORS.NS","Auto",    "Auto OEM",        "Auto"),
    (53, "Maruti Suzuki",     "MARUTI.NS",   "Auto",     "Auto OEM",        "Auto"),
    (54, "M&M",               "M&M.NS",      "Auto",     "Auto OEM",        "Auto"),
    (55, "Hero MotoCorp",     "HEROMOTOCO.NS","Auto",    "Two Wheelers",    "Auto"),
    (56, "Bajaj Auto",        "BAJAJ-AUTO.NS","Auto",    "Two Wheelers",    "Auto"),
    (57, "Eicher Motors",     "EICHERMOT.NS","Auto",     "Two Wheelers",    "Auto"),
    (58, "TVS Motor",         "TVSMOTOR.NS", "Auto",     "Two Wheelers",    "Auto"),
    (59, "Bosch India",       "BOSCHLTD.NS", "Auto",     "Auto Components", "Auto"),

    # Metals & Mining  (6)
    (60, "Tata Steel",        "TATASTEEL.NS","Metals",   "Steel",           "Metals"),
    (61, "JSW Steel",         "JSWSTEEL.NS", "Metals",   "Steel",           "Metals"),
    (62, "SAIL",              "SAIL.NS",     "Metals",   "Steel",           "Metals"),
    (63, "Hindalco",          "HINDALCO.NS", "Metals",   "Aluminium",       "Metals"),
    (64, "Vedanta",           "VEDL.NS",     "Metals",   "Diversified Metals","Metals"),
    (65, "Coal India",        "COALINDIA.NS","Metals",   "Mining",          "Metals"),

    # Energy & Oil  (6)
    (66, "Reliance Ind",      "RELIANCE.NS", "Energy",   "Oil & Gas",       "Energy"),
    (67, "ONGC",              "ONGC.NS",     "Energy",   "Oil & Gas",       "Energy"),
    (68, "BPCL",              "BPCL.NS",     "Energy",   "Oil Refining",    "Energy"),
    (69, "IOC",               "IOC.NS",      "Energy",   "Oil Refining",    "Energy"),
    (70, "Power Grid",        "POWERGRID.NS","Energy",   "Power T&D",       "Energy"),
    (71, "NTPC",              "NTPC.NS",     "Energy",   "Power Generation", "Energy"),

    # Infrastructure / Capital Goods  (6)
    (72, "Larsen & Toubro",   "LT.NS",       "Infra",    "Engineering EPC", "Capital Goods"),
    (73, "Adani Ports",       "ADANIPORTS.NS","Infra",   "Ports",           "Infra"),
    (74, "ABB India",         "ABB.NS",      "Infra",    "Capital Goods",   "Capital Goods"),
    (75, "Siemens India",     "SIEMENS.NS",  "Infra",    "Capital Goods",   "Capital Goods"),
    (76, "Bharat Electronics","BEL.NS",      "Infra",    "Defence",         "Capital Goods"),
    (77, "HAL",               "HAL.NS",      "Infra",    "Defence",         "Capital Goods"),

    # Cement  (5)
    (78, "UltraTech Cement",  "ULTRACEMCO.NS","Cement",  "Cement",          "Cement"),
    (79, "Shree Cement",      "SHREECEM.NS", "Cement",   "Cement",          "Cement"),
    (80, "ACC",               "ACC.NS",      "Cement",   "Cement",          "Cement"),
    (81, "Ambuja Cement",     "AMBUJACEM.NS","Cement",   "Cement",          "Cement"),
    (82, "Dalmia Bharat",     "DALBHARAT.NS","Cement",   "Cement",          "Cement"),

    # Consumer Durables  (4)
    (83, "Havells India",     "HAVELLS.NS",  "Consumer", "Consumer Durables","Consumer"),
    (84, "Voltas",            "VOLTAS.NS",   "Consumer", "Consumer Durables","Consumer"),
    (85, "Whirlpool India",   "WHIRLPOOL.NS","Consumer", "Consumer Durables","Consumer"),
    (86, "Blue Star",         "BLUESTARCO.NS","Consumer","Consumer Durables","Consumer"),

    # Telecom  (3)
    (87, "Bharti Airtel",     "BHARTIARTL.NS","Telecom", "Telecom",         "Telecom"),
    (88, "Indus Towers",      "INDUSTOWER.NS","Telecom", "Telecom Infra",   "Telecom"),
    (89, "MTNL",              "MTNL.NS",     "Telecom",  "Telecom",         "Telecom"),

    # Healthcare Services  (3)
    (90, "Apollo Hospitals",  "APOLLOHOSP.NS","Healthcare","Hospitals",     "Healthcare"),
    (91, "Fortis Healthcare", "FORTIS.NS",   "Healthcare","Hospitals",      "Healthcare"),
    (92, "Max Healthcare",    "MAXHEALTH.NS","Healthcare","Hospitals",      "Healthcare"),
]

# Profile: (base_sales_cr, sales_growth_mean, sales_growth_std,
#           base_npm, npm_std, de_ratio, capex_pct, cfo_pat_ratio)
SECTOR_PROFILES = {
    "Technology":  (40000, 0.14, 0.05, 0.20, 0.03, 0.02, 0.03, 1.15),
    "Financials":  (15000, 0.17, 0.08, 0.22, 0.05, 4.50, 0.01, 0.85),
    "FMCG":        (12000, 0.10, 0.04, 0.14, 0.03, 0.15, 0.05, 1.10),
    "Pharma":      (8000,  0.12, 0.06, 0.16, 0.04, 0.25, 0.07, 0.95),
    "Auto":        (20000, 0.10, 0.08, 0.07, 0.03, 0.60, 0.08, 0.90),
    "Metals":      (25000, 0.08, 0.12, 0.06, 0.05, 1.20, 0.10, 0.80),
    "Energy":      (80000, 0.09, 0.07, 0.05, 0.03, 0.80, 0.12, 0.88),
    "Infra":       (30000, 0.12, 0.07, 0.08, 0.03, 1.50, 0.12, 0.75),
    "Cement":      (10000, 0.11, 0.06, 0.10, 0.04, 0.60, 0.15, 0.85),
    "Consumer":    (6000,  0.12, 0.05, 0.08, 0.03, 0.20, 0.06, 0.95),
    "Telecom":     (50000, 0.08, 0.09, 0.05, 0.06, 2.50, 0.20, 0.70),
    "Healthcare":  (5000,  0.15, 0.07, 0.06, 0.04, 0.80, 0.10, 0.80),
}

YEARS = list(range(2010, 2025))  # FY2010 – FY2024  (15 years)


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate_financials(company_id: int, sector: str, base_sales_cr: float, rng) -> list[dict]:
    """Generate 15 years of realistic financials for one company."""
    profile = SECTOR_PROFILES.get(sector, SECTOR_PROFILES["Technology"])
    (_, g_mean, g_std, base_npm, npm_std, base_de, capex_pct, cfo_pat_ratio) = profile

    # Scale base_sales by a company-level multiplier so companies differ
    scale = rng.uniform(0.3, 2.0)
    sales = base_sales_cr * scale
    de_ratio = max(0, base_de * rng.uniform(0.5, 1.8))
    rows = []

    for i, year in enumerate(YEARS):
        g = rng.normal(g_mean, g_std)
        if i > 0:
            sales = sales * (1 + g)
        sales = max(100, sales)

        npm = _clamp(rng.normal(base_npm, npm_std), -0.15, 0.45)
        net_profit = sales * npm

        opm_base = npm + rng.uniform(0.04, 0.08)  # OPM typically > NPM
        opm_base = _clamp(opm_base, 0.01, 0.55)
        operating_profit = sales * opm_base
        opm_percentage = round(opm_base * 100, 2)

        # Equity & Balance Sheet
        if sector == "Financials":
            equity_capital = sales * 0.05 * rng.uniform(0.8, 1.2)
            reserves = sales * rng.uniform(0.8, 2.0)
            borrowings = (equity_capital + reserves) * de_ratio * rng.uniform(0.85, 1.15)
        else:
            equity_capital = sales * 0.04 * rng.uniform(0.7, 1.3)
            reserves = sales * rng.uniform(0.3, 1.2)
            borrowings = (equity_capital + reserves) * de_ratio * rng.uniform(0.7, 1.3)

        total_equity = equity_capital + reserves
        total_debt = borrowings

        # Assets & investments
        total_assets = total_equity + borrowings + (sales * rng.uniform(0.1, 0.3))
        investments = borrowings * rng.uniform(0.1, 0.4) if borrowings > 0 else sales * 0.05

        # Interest
        interest_rate = rng.uniform(0.07, 0.11)
        interest = borrowings * interest_rate if borrowings > 1 else 0.0

        other_income = sales * rng.uniform(0.005, 0.025)
        depreciation = sales * rng.uniform(0.02, 0.06)
        ebit = operating_profit + other_income - depreciation

        # Cash flows
        cfo = net_profit * cfo_pat_ratio * rng.uniform(0.85, 1.15)
        capex = -(sales * capex_pct * rng.uniform(0.7, 1.4))
        cfi = capex + investments * rng.uniform(-0.1, 0.1)
        cff = -(cfo + cfi) * rng.uniform(0.3, 0.8)  # variable financing

        # Per-share (assume 50cr shares for large, less for small)
        shares = equity_capital / 1.0  # equity_capital is already in crore units ≈ face value
        shares_m = max(shares, 10)  # at least 10 crore shares
        eps = (net_profit * 100) / shares_m if shares_m > 0 else 0  # in rupees
        book_value_ps = (total_equity * 100) / shares_m if shares_m > 0 else 0

        # Dividend payout
        if net_profit > 0:
            dpayout = rng.uniform(10, 45)
        else:
            dpayout = 0.0

        # Pre-computed reference columns (with slight noise for cross-check testing)
        roe_ref = (net_profit / total_equity * 100) if total_equity > 0 else 0
        ebit_actual = operating_profit  # simplified EBIT
        capital_employed = total_equity + borrowings
        roce_ref = (ebit_actual / capital_employed * 100) if capital_employed > 0 else 0

        # Inject anomaly: TCS (company_id=1) has a suspiciously low source ROE in some years
        if company_id == 1 and year in (2015, 2018):
            roe_ref = 0.52  # intentional source data anomaly for edge-case testing

        rows.append({
            "company_id": company_id,
            "year": year,
            "sales": round(sales, 2),
            "operating_profit": round(operating_profit, 2),
            "opm_percentage": opm_percentage,
            "other_income": round(other_income, 2),
            "interest": round(interest, 2),
            "depreciation": round(depreciation, 2),
            "net_profit": round(net_profit, 2),
            "equity_capital": round(equity_capital, 2),
            "reserves": round(reserves, 2),
            "borrowings": round(borrowings, 2),
            "total_assets": round(total_assets, 2),
            "investments": round(investments, 2),
            "operating_activity": round(cfo, 2),
            "investing_activity": round(cfi, 2),
            "financing_activity": round(cff, 2),
            "eps": round(eps, 2),
            "book_value_per_share": round(book_value_ps, 2),
            "dividend_payout_ratio_pct": round(dpayout, 2),
            "roce_percentage": round(roce_ref, 2),
            "roe_percentage": round(roe_ref, 2),
        })

    return rows


def main():
    rng = np.random.default_rng(42)

    # ── company master ──
    company_rows = []
    for cid, name, ticker, broad, sector, industry in COMPANIES:
        company_rows.append({
            "company_id": cid,
            "company_name": name,
            "ticker": ticker,
            "broad_sector": broad,
            "sector": sector,
            "industry": industry,
        })
    df_companies = pd.DataFrame(company_rows)

    # ── financials ──
    all_fin = []
    for cid, name, ticker, broad, sector, industry in COMPANIES:
        profile = SECTOR_PROFILES.get(broad, SECTOR_PROFILES["Technology"])
        base_sales = profile[0]
        rows = generate_financials(cid, broad, base_sales, rng)
        all_fin.extend(rows)

    df_fin = pd.DataFrame(all_fin)

    # ── write to Excel ──
    out_path = os.path.join("data", "raw", "companies.xlsx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df_companies.to_excel(writer, sheet_name="companies", index=False)
        df_fin.to_excel(writer, sheet_name="financials", index=False)

    print(f"[OK] {out_path} written")
    print(f"     companies  : {len(df_companies)} rows")
    print(f"     financials : {len(df_fin)} rows  ({len(df_fin)//len(df_companies)} years/company)")


if __name__ == "__main__":
    main()
