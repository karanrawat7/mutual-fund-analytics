"""
tests/kpi/test_cagr.py
──────────────────────
6 unit tests for the CAGR engine edge cases.
"""

import pytest
from src.analytics.cagr import (
    compute_cagr,
    FLAG_DECLINE_TO_LOSS,
    FLAG_TURNAROUND,
    FLAG_BOTH_NEGATIVE,
    FLAG_ZERO_BASE,
    FLAG_INSUFFICIENT,
)


# ── 13. Normal CAGR ───────────────────────────
def test_cagr_normal():
    """100 → 161.051 in 5 years ≈ 10% CAGR."""
    cagr_val, flag = compute_cagr(100, 161.051, 5)
    assert flag is None
    assert cagr_val == pytest.approx(10.0, abs=0.1)


# ── 14. Turnaround ────────────────────────────
def test_cagr_turnaround():
    """Negative start, positive end → TURNAROUND flag."""
    cagr_val, flag = compute_cagr(-50, 100, 5)
    assert cagr_val is None
    assert flag == FLAG_TURNAROUND


# ── 15. Decline to loss ───────────────────────
def test_cagr_decline_to_loss():
    """Positive start, negative end → DECLINE_TO_LOSS flag."""
    cagr_val, flag = compute_cagr(100, -20, 5)
    assert cagr_val is None
    assert flag == FLAG_DECLINE_TO_LOSS


# ── 16. Both negative ─────────────────────────
def test_cagr_both_negative():
    """Both start and end negative → BOTH_NEGATIVE flag."""
    cagr_val, flag = compute_cagr(-50, -30, 3)
    assert cagr_val is None
    assert flag == FLAG_BOTH_NEGATIVE


# ── 17. Zero base ─────────────────────────────
def test_cagr_zero_base():
    """Start value = 0 → ZERO_BASE flag."""
    cagr_val, flag = compute_cagr(0, 100, 5)
    assert cagr_val is None
    assert flag == FLAG_ZERO_BASE


# ── 18. Insufficient data ─────────────────────
def test_cagr_insufficient_data():
    """Years = 0 (or negative) → INSUFFICIENT flag."""
    cagr_val, flag = compute_cagr(100, 200, 0)
    assert cagr_val is None
    assert flag == FLAG_INSUFFICIENT

    cagr_val_neg, flag_neg = compute_cagr(100, 200, -1)
    assert cagr_val_neg is None
    assert flag_neg == FLAG_INSUFFICIENT
