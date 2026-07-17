"""
src/analytics/cashflow_kpis.py
──────────────────────────────
Cash-flow KPIs: Free Cash Flow, CFO Quality, CapEx Intensity,
FCF Conversion, and Capital Allocation 8-pattern classifier.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# CFO/PAT threshold for "Shareholder Returns" variant of (+,-,-)
_CFO_PAT_SHAREHOLDER_THRESHOLD = 1.2


# ──────────────────────────────────────────────
#  SINGLE-YEAR KPIs
# ──────────────────────────────────────────────

def free_cash_flow(operating_activity: float, investing_activity: float) -> float:
    """FCF = CFO + CFI.  Negative values are allowed."""
    return operating_activity + investing_activity


def capex_intensity(
    investing_activity: float,
    sales: float,
) -> Tuple[Optional[float], Optional[str]]:
    """CapEx Intensity = abs(investing_activity) / sales × 100.

    Returns (percentage, label).
    Labels: 'Asset Light' (<3%), 'Moderate' (3-8%), 'Capital Intensive' (>8%).
    Returns (None, None) if sales is zero.
    """
    if sales == 0:
        return None, None

    pct = abs(investing_activity) / sales * 100

    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return round(pct, 4), label


def fcf_conversion_rate(
    fcf: float,
    operating_profit: float,
) -> Optional[float]:
    """FCF Conversion Rate = FCF / operating_profit × 100.

    Returns None if operating_profit is zero.
    """
    if operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100


def capital_allocation_pattern(
    cfo: float,
    cfi: float,
    cff: float,
    cfo_pat_ratio: Optional[float] = None,
) -> str:
    """Classify capital allocation into one of 8 patterns based on
    the sign of (CFO, CFI, CFF).

    Pattern table:
        (+,-,-)  Reinvestor  (or Shareholder Returns if high CFO/PAT)
        (+,+,-)  Liquidating Assets
        (-,+,+)  Distress Signal
        (-,-,+)  Growth Funded by Debt
        (+,+,+)  Cash Accumulator
        (-,-,-)  Pre-Revenue
        (+,-,+)  Mixed
        other    Mixed (fallback)
    """
    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-",
    )

    pattern_map = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    label = pattern_map.get(signs, "Mixed")

    # Shareholder Returns variant for (+,-,-)
    if signs == ("+", "-", "-") and cfo_pat_ratio is not None:
        if cfo_pat_ratio > _CFO_PAT_SHAREHOLDER_THRESHOLD:
            label = "Shareholder Returns"

    return label


# ──────────────────────────────────────────────
#  MULTI-YEAR KPIs
# ──────────────────────────────────────────────

def cfo_quality_score(
    financials_df: pd.DataFrame,
    current_year: int,
    lookback_years: int = 5,
) -> Tuple[Optional[float], Optional[str]]:
    """CFO Quality Score = average of (CFO / PAT) over the last *lookback_years*.

    Labels:
        > 1.0  → 'High Quality'
        0.5–1.0 → 'Moderate'
        < 0.5  → 'Accrual Risk'

    Returns (score, label).  Returns (None, None) if PAT is zero in all
    lookback years or if insufficient data.
    """
    start_year = current_year - lookback_years + 1
    window = financials_df[
        (financials_df["year"] >= start_year) &
        (financials_df["year"] <= current_year)
    ].copy()

    if window.empty:
        return None, None

    # Filter out years where PAT == 0 to avoid division error
    valid = window[window["net_profit"] != 0]
    if valid.empty:
        return None, None

    ratios = valid["operating_activity"] / valid["net_profit"]
    avg_score = ratios.mean()

    if avg_score > 1.0:
        label = "High Quality"
    elif avg_score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return round(avg_score, 4), label
