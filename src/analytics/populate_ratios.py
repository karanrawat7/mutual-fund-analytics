"""
src/analytics/populate_ratios.py
────────────────────────────────
Orchestrator: runs the full ratio engine for all 92 companies across
all available years and writes into the ``financial_ratios`` table.

Also generates output/capital_allocation.csv.

Run:
    python -m src.analytics.populate_ratios
"""

from __future__ import annotations

import csv
import logging
import os
import sqlite3
from typing import Any, Dict, List, Optional

import pandas as pd

# ── project imports ──────────────────────────
from src.analytics import ratios, cagr, cashflow_kpis

DB_PATH  = os.path.join("database", "bluestock_mf.db")
OUT_DIR  = "output"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
#  COMPOSITE QUALITY SCORE
# ──────────────────────────────────────────────

def _normalise(value: Optional[float], lo: float, hi: float) -> Optional[float]:
    """Min-max normalise *value* to 0–100.  Clamps at boundaries."""
    if value is None:
        return None
    clamped = max(lo, min(hi, value))
    if hi == lo:
        return 50.0
    return (clamped - lo) / (hi - lo) * 100


def composite_quality_score(
    roe: Optional[float],
    revenue_cagr_5yr: Optional[float],
    de_ratio: Optional[float],
    icr: Optional[float],
    cfo_quality: Optional[float],
    fcf_conversion: Optional[float],
) -> Optional[float]:
    """Weighted average of normalised sub-scores.

    Weights: ROE 20%, CAGR 20%, inv-D/E 15%, ICR 15%, CFO quality 15%,
             FCF conversion 15%.
    """
    sub = {
        "roe":            (_normalise(roe, 0, 40),              0.20),
        "rev_cagr":       (_normalise(revenue_cagr_5yr, -10, 30), 0.20),
        "inv_de":         (_normalise(100 - (de_ratio or 0) * 10, 0, 100), 0.15),
        "icr":            (_normalise(icr, 0, 20),               0.15),
        "cfo_quality":    (_normalise(cfo_quality, 0, 2),        0.15),
        "fcf_conversion": (_normalise(fcf_conversion, 0, 150),   0.15),
    }

    total_weight = 0.0
    weighted_sum = 0.0
    for _name, (score, weight) in sub.items():
        if score is not None:
            weighted_sum += score * weight
            total_weight += weight

    if total_weight == 0:
        return None
    return round(weighted_sum / total_weight, 2)


# ──────────────────────────────────────────────
#  MAIN PIPELINE
# ──────────────────────────────────────────────

def _load_data(conn: sqlite3.Connection):
    """Load company master and financials into DataFrames."""
    df_companies = pd.read_sql("SELECT * FROM companies", conn)
    df_financials = pd.read_sql("SELECT * FROM company_financials", conn)
    return df_companies, df_financials


def _compute_ratios_for_company(
    company_id: int,
    broad_sector: str,
    company_name: str,
    company_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """Compute all KPIs for one company across all years."""
    company_df = company_df.sort_values("year").reset_index(drop=True)
    rows: List[Dict[str, Any]] = []

    for _, row in company_df.iterrows():
        year = int(row["year"])

        # ── Profitability ─────────────────────
        npm = ratios.net_profit_margin(row["net_profit"], row["sales"])
        opm = ratios.operating_profit_margin(row["operating_profit"], row["sales"])
        roe = ratios.return_on_equity(
            row["net_profit"], row["equity_capital"], row["reserves"],
        )

        # EBIT approximation: operating_profit + other_income - depreciation
        ebit = row["operating_profit"] + row["other_income"] - row["depreciation"]
        roce = ratios.return_on_capital_employed(
            ebit, row["equity_capital"], row["reserves"], row["borrowings"],
        )
        roa = ratios.return_on_assets(row["net_profit"], row["total_assets"])

        # OPM cross-check (log only, don't modify value)
        ratios.cross_check_opm(opm, row["opm_percentage"], company_name, year)

        # ── Leverage / Efficiency ─────────────
        de = ratios.debt_to_equity(
            row["borrowings"], row["equity_capital"], row["reserves"],
        )
        hl_flag = ratios.high_leverage_flag(de, broad_sector)
        icr = ratios.interest_coverage(
            row["operating_profit"], row["other_income"], row["interest"],
        )
        icr_lbl = ratios.icr_label(row["interest"], icr)
        icr_warn = ratios.icr_warning_flag(icr)
        nd = ratios.net_debt(row["borrowings"], row["investments"])
        at = ratios.asset_turnover(row["sales"], row["total_assets"])

        # ── Cash Flow KPIs ────────────────────
        fcf = cashflow_kpis.free_cash_flow(
            row["operating_activity"], row["investing_activity"],
        )
        capex_pct, capex_label = cashflow_kpis.capex_intensity(
            row["investing_activity"], row["sales"],
        )
        fcf_conv = cashflow_kpis.fcf_conversion_rate(fcf, row["operating_profit"])

        # CFO/PAT ratio for current year (for capital allocation)
        pat = row["net_profit"]
        cfo_pat = (row["operating_activity"] / pat) if pat != 0 else None

        cap_pattern = cashflow_kpis.capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"],
            cfo_pat_ratio=cfo_pat,
        )

        # CFO Quality Score (multi-year)
        cfo_score, cfo_label = cashflow_kpis.cfo_quality_score(
            company_df, year, lookback_years=5,
        )

        # ── CAGR ──────────────────────────────
        rev_cagr  = cagr.revenue_cagr(company_df, year)
        pat_cagr_ = cagr.pat_cagr(company_df, year)
        eps_cagr_ = cagr.eps_cagr(company_df, year)

        # ── Composite Score ───────────────────
        cqs = composite_quality_score(
            roe=roe,
            revenue_cagr_5yr=rev_cagr.get("revenue_cagr_5yr"),
            de_ratio=de,
            icr=icr,
            cfo_quality=cfo_score,
            fcf_conversion=fcf_conv,
        )

        # ── Assemble row ──────────────────────
        ratio_row: Dict[str, Any] = {
            "company_id": company_id,
            "year": year,
            # profitability
            "net_profit_margin_pct": _rd(npm),
            "operating_profit_margin_pct": _rd(opm),
            "return_on_equity_pct": _rd(roe),
            "return_on_capital_employed_pct": _rd(roce),
            "return_on_assets_pct": _rd(roa),
            # leverage
            "debt_to_equity": _rd(de),
            "high_leverage_flag": 1 if hl_flag else 0,
            "interest_coverage": _rd(icr),
            "icr_label": icr_lbl,
            "icr_warning_flag": 1 if icr_warn else 0,
            "net_debt_cr": _rd(nd),
            "asset_turnover": _rd(at),
            # cash flow
            "free_cash_flow_cr": _rd(fcf),
            "capex_cr": _rd(abs(row["investing_activity"])),
            "cash_from_operations_cr": _rd(row["operating_activity"]),
            "cfo_quality_score": _rd(cfo_score),
            "cfo_quality_label": cfo_label,
            "capex_intensity_pct": _rd(capex_pct),
            "capex_intensity_label": capex_label,
            "fcf_conversion_rate": _rd(fcf_conv),
            "capital_allocation_pattern": cap_pattern,
            # per-share
            "earnings_per_share": _rd(row["eps"]),
            "book_value_per_share": _rd(row["book_value_per_share"]),
            "dividend_payout_ratio_pct": _rd(row["dividend_payout_ratio_pct"]),
            "total_debt_cr": _rd(row["borrowings"]),
            # CAGR - Revenue
            "revenue_cagr_3yr":      _rd(rev_cagr.get("revenue_cagr_3yr")),
            "revenue_cagr_3yr_flag": rev_cagr.get("revenue_cagr_3yr_flag"),
            "revenue_cagr_5yr":      _rd(rev_cagr.get("revenue_cagr_5yr")),
            "revenue_cagr_5yr_flag": rev_cagr.get("revenue_cagr_5yr_flag"),
            "revenue_cagr_10yr":     _rd(rev_cagr.get("revenue_cagr_10yr")),
            "revenue_cagr_10yr_flag": rev_cagr.get("revenue_cagr_10yr_flag"),
            # CAGR - PAT
            "pat_cagr_3yr":      _rd(pat_cagr_.get("pat_cagr_3yr")),
            "pat_cagr_3yr_flag": pat_cagr_.get("pat_cagr_3yr_flag"),
            "pat_cagr_5yr":      _rd(pat_cagr_.get("pat_cagr_5yr")),
            "pat_cagr_5yr_flag": pat_cagr_.get("pat_cagr_5yr_flag"),
            "pat_cagr_10yr":     _rd(pat_cagr_.get("pat_cagr_10yr")),
            "pat_cagr_10yr_flag": pat_cagr_.get("pat_cagr_10yr_flag"),
            # CAGR - EPS
            "eps_cagr_3yr":      _rd(eps_cagr_.get("eps_cagr_3yr")),
            "eps_cagr_3yr_flag": eps_cagr_.get("eps_cagr_3yr_flag"),
            "eps_cagr_5yr":      _rd(eps_cagr_.get("eps_cagr_5yr")),
            "eps_cagr_5yr_flag": eps_cagr_.get("eps_cagr_5yr_flag"),
            "eps_cagr_10yr":     _rd(eps_cagr_.get("eps_cagr_10yr")),
            "eps_cagr_10yr_flag": eps_cagr_.get("eps_cagr_10yr_flag"),
            # composite
            "composite_quality_score": _rd(cqs),
        }
        rows.append(ratio_row)

    return rows


def _rd(v: Optional[float]) -> Optional[float]:
    """Round to 4 decimals if not None."""
    if v is None:
        return None
    return round(v, 4)


def _write_to_db(conn: sqlite3.Connection, all_rows: List[Dict[str, Any]]) -> int:
    """Insert all ratio rows into the financial_ratios table."""
    if not all_rows:
        return 0

    columns = list(all_rows[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_str = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO financial_ratios ({col_str}) VALUES ({placeholders})"

    cur = conn.cursor()
    cur.execute("DELETE FROM financial_ratios")  # fresh load
    for row in all_rows:
        cur.execute(sql, [row[c] for c in columns])
    conn.commit()
    return len(all_rows)


def _write_capital_allocation_csv(
    all_rows: List[Dict[str, Any]],
    df_financials: pd.DataFrame,
) -> str:
    """Generate output/capital_allocation.csv."""
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "capital_allocation.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label",
        ])
        for row in all_rows:
            # Recover signs from the financials
            cid, yr = row["company_id"], row["year"]
            fin = df_financials[
                (df_financials["company_id"] == cid) &
                (df_financials["year"] == yr)
            ]
            if fin.empty:
                continue
            fr = fin.iloc[0]
            writer.writerow([
                cid, yr,
                "+" if fr["operating_activity"] >= 0 else "-",
                "+" if fr["investing_activity"] >= 0 else "-",
                "+" if fr["financing_activity"] >= 0 else "-",
                row["capital_allocation_pattern"],
            ])

    return out_path


def main():
    """Entry point — run the full ratio engine."""
    conn = sqlite3.connect(DB_PATH)
    df_companies, df_financials = _load_data(conn)

    logger.info(
        "Loaded %d companies, %d financial records",
        len(df_companies), len(df_financials),
    )

    all_rows: List[Dict[str, Any]] = []

    for _, co in df_companies.iterrows():
        cid = int(co["company_id"])
        company_df = df_financials[df_financials["company_id"] == cid].copy()

        if company_df.empty:
            logger.warning("No financials for company_id=%d (%s)", cid, co["company_name"])
            continue

        rows = _compute_ratios_for_company(
            company_id=cid,
            broad_sector=co["broad_sector"],
            company_name=co["company_name"],
            company_df=company_df,
        )
        all_rows.extend(rows)

    # ── Write to DB ───────────────────────────
    count = _write_to_db(conn, all_rows)
    logger.info("[OK] financial_ratios populated: %d rows", count)

    # ── Verify ────────────────────────────────
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM financial_ratios")
    db_count = cur.fetchone()[0]
    logger.info("Verification: SELECT COUNT(*) FROM financial_ratios = %d", db_count)

    # ── Capital allocation CSV ────────────────
    csv_path = _write_capital_allocation_csv(all_rows, df_financials)
    logger.info("[OK] %s written (%d rows)", csv_path, len(all_rows))

    # ── Null-only column check ────────────────
    ratio_df = pd.read_sql("SELECT * FROM financial_ratios", conn)
    null_only = [c for c in ratio_df.columns if ratio_df[c].isna().all()]
    if null_only:
        logger.warning("NULL-only columns: %s", null_only)
    else:
        logger.info("[OK] No null-only columns found")

    conn.close()
    logger.info("Done.")


if __name__ == "__main__":
    main()
