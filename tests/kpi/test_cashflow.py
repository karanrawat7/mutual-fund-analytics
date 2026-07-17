"""
tests/kpi/test_cashflow.py
──────────────────────────
2 unit tests for cash-flow KPI functions.
"""

import pytest
from src.analytics.cashflow_kpis import (
    fcf_conversion_rate,
    capital_allocation_pattern,
)


# ── 19. FCF conversion — zero operating profit ─
def test_fcf_conversion_zero_op_profit():
    """Operating profit = 0 → returns None."""
    result = fcf_conversion_rate(500, 0)
    assert result is None


# ── 20. Capital allocation — Reinvestor ────────
def test_capital_allocation_reinvestor():
    """CFO > 0, CFI < 0, CFF < 0 → 'Reinvestor'."""
    label = capital_allocation_pattern(
        cfo=1000, cfi=-500, cff=-300, cfo_pat_ratio=0.9,
    )
    assert label == "Reinvestor"

    # With high CFO/PAT → Shareholder Returns
    label_sr = capital_allocation_pattern(
        cfo=1000, cfi=-500, cff=-300, cfo_pat_ratio=1.5,
    )
    assert label_sr == "Shareholder Returns"
