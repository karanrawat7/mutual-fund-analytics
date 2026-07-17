"""
src/analytics/ratios.py
─────────────────────────
Profitability, leverage, and efficiency ratio functions.

Every function is a pure computation — accepts raw values,
returns the computed KPI or None for edge cases.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
#  PROFITABILITY RATIOS  (Day 08)
# ──────────────────────────────────────────────

def net_profit_margin(net_profit: float, sales: float) -> Optional[float]:
    """Net Profit Margin = net_profit / sales × 100.

    Returns None if sales is zero (undefined).
    """
    if sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit: float, sales: float) -> Optional[float]:
    """Operating Profit Margin = operating_profit / sales × 100.

    Returns None if sales is zero.
    """
    if sales == 0:
        return None
    return (operating_profit / sales) * 100


def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float,
) -> Optional[float]:
    """ROE = net_profit / (equity_capital + reserves) × 100.

    Returns None if equity + reserves <= 0 (negative or zero equity).
    """
    total_equity = equity_capital + reserves
    if total_equity <= 0:
        return None
    return (net_profit / total_equity) * 100


def return_on_capital_employed(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
) -> Optional[float]:
    """ROCE = EBIT / (equity + reserves + borrowings) × 100.

    Returns None if capital employed <= 0.
    """
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return (ebit / capital_employed) * 100


def return_on_assets(net_profit: float, total_assets: float) -> Optional[float]:
    """ROA = net_profit / total_assets × 100.

    Returns None if total_assets is zero.
    """
    if total_assets == 0:
        return None
    return (net_profit / total_assets) * 100


def cross_check_opm(
    computed_opm: Optional[float],
    source_opm: Optional[float],
    company_name: str = "",
    year: int = 0,
) -> Tuple[bool, Optional[float]]:
    """Compare computed OPM against the source opm_percentage field.

    Logs a warning if the absolute difference exceeds 1 percentage point.
    Returns (match, diff) where match is True if within tolerance.
    """
    if computed_opm is None or source_opm is None:
        return True, None

    diff = abs(computed_opm - source_opm)
    match = diff <= 1.0

    if not match:
        logger.warning(
            "OPM mismatch for %s (%d): computed=%.2f%%, source=%.2f%%, diff=%.2f pp",
            company_name, year, computed_opm, source_opm, diff,
        )

    return match, round(diff, 4)


# ──────────────────────────────────────────────
#  LEVERAGE & EFFICIENCY RATIOS  (Day 09)
# ──────────────────────────────────────────────

def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float,
) -> Optional[float]:
    """D/E = borrowings / (equity_capital + reserves).

    Returns 0.0 (not None) if borrowings is zero — the company is debt-free.
    Returns None only if equity is zero or negative.
    """
    if borrowings == 0:
        return 0.0
    total_equity = equity_capital + reserves
    if total_equity <= 0:
        return None
    return borrowings / total_equity


def high_leverage_flag(de_ratio: Optional[float], broad_sector: str) -> bool:
    """Flag companies with D/E > 5 that are NOT in the Financials sector.

    Financials sector companies are structurally leveraged, so the flag
    is suppressed for them.
    """
    if de_ratio is None:
        return False
    if broad_sector == "Financials":
        return False
    return de_ratio > 5.0


def interest_coverage(
    operating_profit: float,
    other_income: float,
    interest: float,
) -> Optional[float]:
    """ICR = (operating_profit + other_income) / interest.

    Returns None if interest is zero (debt-free company).
    """
    if interest == 0:
        return None
    return (operating_profit + other_income) / interest


def icr_label(interest: float, icr_value: Optional[float]) -> Optional[str]:
    """Return descriptive ICR label.

    - 'Debt Free'  when interest is zero
    - 'Strong'     when ICR >= 3
    - 'Adequate'   when 1.5 <= ICR < 3
    - 'Weak'       when ICR < 1.5
    """
    if interest == 0:
        return "Debt Free"
    if icr_value is None:
        return None
    if icr_value >= 3:
        return "Strong"
    if icr_value >= 1.5:
        return "Adequate"
    return "Weak"


def icr_warning_flag(icr_value: Optional[float]) -> bool:
    """Flag companies at risk of not covering interest payments (ICR < 1.5)."""
    if icr_value is None:
        return False
    return icr_value < 1.5


def net_debt(borrowings: float, investments: float) -> float:
    """Net Debt = borrowings - investments.

    Negative values are allowed (company has more liquid assets than debt).
    """
    return borrowings - investments


def asset_turnover(sales: float, total_assets: float) -> Optional[float]:
    """Asset Turnover = sales / total_assets.

    Returns None if total_assets is zero.
    """
    if total_assets == 0:
        return None
    return sales / total_assets
