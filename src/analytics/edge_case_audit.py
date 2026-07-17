"""
src/analytics/edge_case_audit.py
────────────────────────────────
ROCE / ROE cross-checks against source data (companies.xlsx reference
columns stored in company_financials).

Generates output/ratio_edge_cases.log with documented anomalies.

Run:
    python -m src.analytics.edge_case_audit
"""

from __future__ import annotations

import csv
import logging
import os
import sqlite3

import pandas as pd

DB_PATH = os.path.join("database", "bluestock_mf.db")
OUT_DIR = "output"
LOG_FILE = os.path.join(OUT_DIR, "ratio_edge_cases.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# Anomaly categories
CAT_DATA_SOURCE   = "DATA_SOURCE_ISSUE"
CAT_VERSION_DIFF  = "VERSION_DIFFERENCE"
CAT_FORMULA_DISC  = "FORMULA_DISCREPANCY"

# Known source-data anomalies (injected in generate_equity_data.py)
KNOWN_ANOMALIES = {
    # (company_id, year): explanation
    (1, 2015): "TCS source ROE intentionally set to 0.52 — known test anomaly",
    (1, 2018): "TCS source ROE intentionally set to 0.52 — known test anomaly",
}


def _categorise_anomaly(
    company_id: int,
    year: int,
    kpi: str,
    diff_pct: float,
) -> str:
    """Determine the anomaly category."""
    # Known source-data issues
    if (company_id, year) in KNOWN_ANOMALIES and kpi == "ROE":
        return CAT_DATA_SOURCE

    # Large discrepancies typically indicate formula difference
    if diff_pct > 20:
        return CAT_FORMULA_DISC

    # Moderate differences are version/rounding differences
    return CAT_VERSION_DIFF


def run_audit():
    """Cross-check computed ratios against source data and generate log."""
    conn = sqlite3.connect(DB_PATH)

    # Load data
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    df_fin = pd.read_sql("SELECT * FROM company_financials", conn)
    df_co = pd.read_sql("SELECT * FROM companies", conn)

    # Merge for lookup
    df = df_ratios.merge(
        df_fin[["company_id", "year", "roce_percentage", "roe_percentage"]],
        on=["company_id", "year"],
        how="left",
    ).merge(
        df_co[["company_id", "company_name"]],
        on="company_id",
        how="left",
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    anomalies = []

    for _, row in df.iterrows():
        cid = int(row["company_id"])
        year = int(row["year"])
        name = row["company_name"]

        # ── ROCE cross-check (threshold: 5%) ──
        computed_roce = row.get("return_on_capital_employed_pct")
        source_roce = row.get("roce_percentage")
        if computed_roce is not None and source_roce is not None:
            diff = abs(computed_roce - source_roce)
            if diff > 5:
                category = _categorise_anomaly(cid, year, "ROCE", diff)
                explanation = KNOWN_ANOMALIES.get((cid, year), "")
                if not explanation:
                    explanation = (
                        f"ROCE diff {diff:.2f} pp — computed uses EBIT "
                        "(op_profit+other_income-depreciation), source may "
                        "use operating_profit directly"
                    )
                anomalies.append({
                    "company": name,
                    "company_id": cid,
                    "year": year,
                    "kpi": "ROCE",
                    "computed": round(computed_roce, 2),
                    "source": round(source_roce, 2),
                    "diff_pct": round(diff, 2),
                    "category": category,
                    "explanation": explanation,
                })

        # ── ROE cross-check (log all diffs > 5%) ──
        computed_roe = row.get("return_on_equity_pct")
        source_roe = row.get("roe_percentage")
        if computed_roe is not None and source_roe is not None:
            diff = abs(computed_roe - source_roe)
            if diff > 5:
                category = _categorise_anomaly(cid, year, "ROE", diff)
                explanation = KNOWN_ANOMALIES.get((cid, year), "")
                if not explanation:
                    explanation = (
                        f"ROE diff {diff:.2f} pp — computed: net_profit/"
                        "(equity+reserves), source value may reflect "
                        "different equity definition or vintage"
                    )
                anomalies.append({
                    "company": name,
                    "company_id": cid,
                    "year": year,
                    "kpi": "ROE",
                    "computed": round(computed_roe, 2),
                    "source": round(source_roe, 2),
                    "diff_pct": round(diff, 2),
                    "category": category,
                    "explanation": explanation,
                })

    # ── Write log ─────────────────────────────
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=" * 90 + "\n")
        f.write("RATIO ENGINE — EDGE CASE AUDIT LOG\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"Total anomalies found: {len(anomalies)}\n\n")

        for a in anomalies:
            f.write("-" * 70 + "\n")
            f.write(f"Company   : {a['company']} (id={a['company_id']})\n")
            f.write(f"Year      : {a['year']}\n")
            f.write(f"KPI       : {a['kpi']}\n")
            f.write(f"Computed  : {a['computed']}\n")
            f.write(f"Source    : {a['source']}\n")
            f.write(f"Diff (pp) : {a['diff_pct']}\n")
            f.write(f"Category  : {a['category']}\n")
            f.write(f"Explain   : {a['explanation']}\n")
            f.write("\n")

        # Summary by category
        f.write("=" * 90 + "\n")
        f.write("SUMMARY BY CATEGORY\n")
        f.write("=" * 90 + "\n")
        from collections import Counter
        cat_counts = Counter(a["category"] for a in anomalies)
        for cat, cnt in cat_counts.most_common():
            f.write(f"  {cat}: {cnt}\n")

        f.write("\n[END OF LOG]\n")

    logger.info("[OK] Edge case audit complete: %d anomalies → %s", len(anomalies), LOG_FILE)
    conn.close()
    return anomalies


def main():
    anomalies = run_audit()
    print(f"\nAudit complete. {len(anomalies)} anomalies written to {LOG_FILE}")


if __name__ == "__main__":
    main()
