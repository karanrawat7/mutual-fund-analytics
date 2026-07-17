"""
tests/kpi/test_ratios.py
────────────────────────
8 unit tests for profitability ratio functions.
"""

import logging
import pytest
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    cross_check_opm,
)


# ── 1. Net Profit Margin — normal ─────────────
def test_net_profit_margin_normal():
    """NPM = 200 / 1000 × 100 = 20%."""
    result = net_profit_margin(200, 1000)
    assert result == pytest.approx(20.0)


# ── 2. Net Profit Margin — zero sales ─────────
def test_net_profit_margin_zero_sales():
    """Sales = 0 → returns None."""
    result = net_profit_margin(200, 0)
    assert result is None


# ── 3. ROE — normal ───────────────────────────
def test_roe_normal():
    """ROE = 500 / (100 + 400) × 100 = 100%."""
    result = return_on_equity(500, 100, 400)
    assert result == pytest.approx(100.0)


# ── 4. ROE — negative equity ──────────────────
def test_roe_negative_equity():
    """Equity + Reserves <= 0 → returns None."""
    result = return_on_equity(500, 50, -100)
    assert result is None
    # Zero equity also returns None
    result_zero = return_on_equity(500, 0, 0)
    assert result_zero is None


# ── 5. OPM cross-check — match ────────────────
def test_opm_cross_check_match():
    """Computed and source within 1% tolerance → match=True."""
    match, diff = cross_check_opm(25.5, 25.0, "TestCo", 2024)
    assert match is True
    assert diff == pytest.approx(0.5)


# ── 6. OPM cross-check — mismatch ─────────────
def test_opm_cross_check_mismatch(caplog):
    """Diff > 1% → match=False, warning logged."""
    with caplog.at_level(logging.WARNING):
        match, diff = cross_check_opm(30.0, 25.0, "TestCo", 2024)
    assert match is False
    assert diff == pytest.approx(5.0)
    assert "OPM mismatch" in caplog.text


# ── 7. ROA — normal ───────────────────────────
def test_roa_normal():
    """ROA = 150 / 3000 × 100 = 5%."""
    result = return_on_assets(150, 3000)
    assert result == pytest.approx(5.0)


# ── 8. ROCE — normal ──────────────────────────
def test_roce_normal():
    """ROCE = 300 / (100 + 400 + 500) × 100 = 30%."""
    result = return_on_capital_employed(300, 100, 400, 500)
    assert result == pytest.approx(30.0)
