"""
src/analytics/cagr.py
─────────────────────
CAGR (Compound Annual Growth Rate) engine with full edge-case handling.

Computes Revenue, PAT, and EPS CAGR for 3-year, 5-year, and 10-year windows.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# ── Edge-case flag constants ──────────────────
FLAG_DECLINE_TO_LOSS = "DECLINE_TO_LOSS"   # positive start → negative end
FLAG_TURNAROUND      = "TURNAROUND"        # negative start → positive end
FLAG_BOTH_NEGATIVE   = "BOTH_NEGATIVE"     # both start and end are negative
FLAG_ZERO_BASE       = "ZERO_BASE"         # start value is zero
FLAG_INSUFFICIENT    = "INSUFFICIENT"      # less than n years of data


def compute_cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> Tuple[Optional[float], Optional[str]]:
    """Core CAGR formula with 6 edge-case handlers.

    Returns (cagr_percentage, flag).
    - Normal case: (value, None)
    - Edge case:   (None, FLAG_*)
    """
    if years <= 0:
        return None, FLAG_INSUFFICIENT

    # Zero base
    if start_value == 0:
        return None, FLAG_ZERO_BASE

    # Sign analysis
    start_positive = start_value > 0
    end_positive   = end_value > 0

    if start_positive and end_positive:
        # Normal case — both positive
        cagr = ((end_value / start_value) ** (1.0 / years) - 1) * 100
        return round(cagr, 4), None

    if start_positive and not end_positive:
        return None, FLAG_DECLINE_TO_LOSS

    if not start_positive and end_positive:
        return None, FLAG_TURNAROUND

    # Both negative
    return None, FLAG_BOTH_NEGATIVE


def _extract_cagr_for_metric(
    financials_df: pd.DataFrame,
    metric_col: str,
    current_year: int,
    windows: List[int] = None,
) -> Dict[str, Optional[float | str]]:
    """Compute CAGR for a single metric across multiple time windows.

    Parameters
    ----------
    financials_df : DataFrame
        Must have columns 'year' and *metric_col*, sorted by year.
        Should contain all available years for ONE company.
    metric_col : str
        The column name (e.g. 'sales', 'net_profit', 'eps').
    current_year : int
        The year we are computing for (the "end" year).
    windows : list[int]
        CAGR windows in years, default [3, 5, 10].

    Returns
    -------
    dict  e.g. {"revenue_cagr_3yr": 12.5, "revenue_cagr_3yr_flag": None, ...}
    """
    if windows is None:
        windows = [3, 5, 10]

    # Map metric_col to output prefix
    prefix_map = {
        "sales": "revenue_cagr",
        "net_profit": "pat_cagr",
        "eps": "eps_cagr",
    }
    prefix = prefix_map.get(metric_col, f"{metric_col}_cagr")

    # Build year → value lookup
    year_vals = dict(zip(financials_df["year"], financials_df[metric_col]))

    results: Dict[str, Optional[float | str]] = {}

    for n in windows:
        key_val  = f"{prefix}_{n}yr"
        key_flag = f"{prefix}_{n}yr_flag"

        start_year = current_year - n
        start_val  = year_vals.get(start_year)
        end_val    = year_vals.get(current_year)

        if start_val is None or end_val is None:
            results[key_val]  = None
            results[key_flag] = FLAG_INSUFFICIENT
        else:
            cagr_val, flag = compute_cagr(start_val, end_val, n)
            results[key_val]  = cagr_val
            results[key_flag] = flag

    return results


def revenue_cagr(
    financials_df: pd.DataFrame,
    current_year: int,
    windows: List[int] = None,
) -> Dict[str, Optional[float | str]]:
    """Compute Revenue CAGR for 3, 5, 10-year windows."""
    return _extract_cagr_for_metric(financials_df, "sales", current_year, windows)


def pat_cagr(
    financials_df: pd.DataFrame,
    current_year: int,
    windows: List[int] = None,
) -> Dict[str, Optional[float | str]]:
    """Compute PAT (Net Profit) CAGR for 3, 5, 10-year windows."""
    return _extract_cagr_for_metric(financials_df, "net_profit", current_year, windows)


def eps_cagr(
    financials_df: pd.DataFrame,
    current_year: int,
    windows: List[int] = None,
) -> Dict[str, Optional[float | str]]:
    """Compute EPS CAGR for 3, 5, 10-year windows."""
    return _extract_cagr_for_metric(financials_df, "eps", current_year, windows)
