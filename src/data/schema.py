"""
src/data/schema.py
──────────────────
Creates / migrates the three equity-analytics tables in the existing
bluestock_mf.db SQLite database:

    companies            – 92-row company master
    company_financials   – raw annual P&L / BS / CF data
    financial_ratios     – 40+ computed KPI columns per company-year

Run:
    python -m src.data.schema
    -- or --
    python src/data/schema.py
"""

from __future__ import annotations

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join("database", "bluestock_mf.db")
EXCEL_PATH = os.path.join("data", "raw", "companies.xlsx")


DDL_COMPANIES = """
CREATE TABLE IF NOT EXISTS companies (
    company_id      INTEGER PRIMARY KEY,
    company_name    TEXT NOT NULL,
    ticker          TEXT,
    broad_sector    TEXT,
    sector          TEXT,
    industry        TEXT
);
"""

DDL_COMPANY_FINANCIALS = """
CREATE TABLE IF NOT EXISTS company_financials (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id              INTEGER NOT NULL,
    year                    INTEGER NOT NULL,
    sales                   REAL,
    operating_profit        REAL,
    opm_percentage          REAL,
    other_income            REAL,
    interest                REAL,
    depreciation            REAL,
    net_profit              REAL,
    equity_capital          REAL,
    reserves                REAL,
    borrowings              REAL,
    total_assets            REAL,
    investments             REAL,
    operating_activity      REAL,
    investing_activity      REAL,
    financing_activity      REAL,
    eps                     REAL,
    book_value_per_share    REAL,
    dividend_payout_ratio_pct REAL,
    roce_percentage         REAL,
    roe_percentage          REAL,
    UNIQUE (company_id, year)
);
"""

DDL_FINANCIAL_RATIOS = """
CREATE TABLE IF NOT EXISTS financial_ratios (
    id                              INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id                      INTEGER NOT NULL,
    year                            INTEGER NOT NULL,

    -- Profitability
    net_profit_margin_pct           REAL,
    operating_profit_margin_pct     REAL,
    return_on_equity_pct            REAL,
    return_on_capital_employed_pct  REAL,
    return_on_assets_pct            REAL,

    -- Leverage
    debt_to_equity                  REAL,
    high_leverage_flag              INTEGER,   -- 0/1
    interest_coverage               REAL,
    icr_label                       TEXT,
    icr_warning_flag                INTEGER,   -- 0/1
    net_debt_cr                     REAL,
    asset_turnover                  REAL,

    -- Cash Flow
    free_cash_flow_cr               REAL,
    capex_cr                        REAL,
    cash_from_operations_cr         REAL,
    cfo_quality_score               REAL,
    cfo_quality_label               TEXT,
    capex_intensity_pct             REAL,
    capex_intensity_label           TEXT,
    fcf_conversion_rate             REAL,
    capital_allocation_pattern      TEXT,

    -- Per-share
    earnings_per_share              REAL,
    book_value_per_share            REAL,
    dividend_payout_ratio_pct       REAL,
    total_debt_cr                   REAL,

    -- CAGR — Revenue
    revenue_cagr_3yr                REAL,
    revenue_cagr_3yr_flag           TEXT,
    revenue_cagr_5yr                REAL,
    revenue_cagr_5yr_flag           TEXT,
    revenue_cagr_10yr               REAL,
    revenue_cagr_10yr_flag          TEXT,

    -- CAGR — PAT
    pat_cagr_3yr                    REAL,
    pat_cagr_3yr_flag               TEXT,
    pat_cagr_5yr                    REAL,
    pat_cagr_5yr_flag               TEXT,
    pat_cagr_10yr                   REAL,
    pat_cagr_10yr_flag              TEXT,

    -- CAGR — EPS
    eps_cagr_3yr                    REAL,
    eps_cagr_3yr_flag               TEXT,
    eps_cagr_5yr                    REAL,
    eps_cagr_5yr_flag               TEXT,
    eps_cagr_10yr                   REAL,
    eps_cagr_10yr_flag              TEXT,

    -- Composite
    composite_quality_score         REAL,

    UNIQUE (company_id, year)
);
"""


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(DDL_COMPANIES + DDL_COMPANY_FINANCIALS + DDL_FINANCIAL_RATIOS)
    conn.commit()
    print("[OK] Tables created / verified")


def load_excel_to_db(conn: sqlite3.Connection) -> None:
    """Read companies.xlsx and insert into SQLite tables."""
    df_co = pd.read_excel(EXCEL_PATH, sheet_name="companies")
    df_fin = pd.read_excel(EXCEL_PATH, sheet_name="financials")

    # ── companies ──
    cur = conn.cursor()
    cur.execute("DELETE FROM companies")
    df_co.to_sql("companies", conn, if_exists="append", index=False)
    print(f"[OK] companies loaded  : {len(df_co)} rows")

    # ── company_financials ──
    cur.execute("DELETE FROM company_financials")
    df_fin.to_sql("company_financials", conn, if_exists="append", index=False)
    conn.commit()
    print(f"[OK] company_financials loaded : {len(df_fin)} rows")


def main():
    conn = get_connection()
    create_tables(conn)
    if os.path.exists(EXCEL_PATH):
        load_excel_to_db(conn)
    else:
        print(f"[WARN] {EXCEL_PATH} not found — run generate_equity_data.py first")
    conn.close()


if __name__ == "__main__":
    main()
