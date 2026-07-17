"""
tests/kpi/test_leverage.py
──────────────────────────
4 unit tests for leverage and efficiency ratio functions.
"""

import pytest
from src.analytics.ratios import (
    debt_to_equity,
    interest_coverage,
    icr_label,
    high_leverage_flag,
)


# ── 9. D/E — debt-free returns 0 ──────────────
def test_de_debt_free_returns_zero():
    """Borrowings = 0 → D/E = 0.0 (not None)."""
    result = debt_to_equity(0, 100, 400)
    assert result == 0.0
    assert result is not None


# ── 10. ICR — zero interest returns None ──────
def test_icr_zero_interest_returns_none():
    """Interest = 0 → ICR = None (debt-free)."""
    result = interest_coverage(500, 50, 0)
    assert result is None


# ── 11. ICR label — Debt Free ─────────────────
def test_icr_label_debt_free():
    """When interest is zero, label = 'Debt Free'."""
    label = icr_label(0, None)
    assert label == "Debt Free"


# ── 12. High D/E flag — non-Financials ────────
def test_high_de_flag_non_financials():
    """D/E > 5 and sector != Financials → flag = True.
    D/E > 5 and sector == Financials → flag = False (suppressed).
    """
    # Non-financials with high leverage
    assert high_leverage_flag(6.0, "Technology") is True
    assert high_leverage_flag(5.5, "Infra") is True

    # Financials — flag suppressed even with very high D/E
    assert high_leverage_flag(10.0, "Financials") is False

    # Below threshold
    assert high_leverage_flag(4.0, "Technology") is False
