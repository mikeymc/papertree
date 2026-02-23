# ABOUTME: Unit tests verifying vectorized Buffett scoring matches the scalar StockEvaluator formulas.
# ABOUTME: Covers all scoring bands and missing-value defaults for ROE, gross_margin, debt_to_earnings.
"""
These tests do NOT require a live DB.
They verify that each vectorized Buffett metric scorer in BatchScoringMixin
produces identical results to StockEvaluator._score_higher_is_better /
_score_lower_is_better for every scoring band and edge case.

Scoring bands (all metrics follow this 4-band structure):
  Higher-is-better (ROE, gross_margin):
    value >= excellent        → 100
    [good, excellent)         → 75-100 (interpolated)
    [fair, good)              → 25-75  (interpolated)   ← was wrong: 50-75
    (0, fair)                 → 0-25   (interpolated)   ← was wrong: 25-50
    <= 0                      → 0
    NaN                       → 0 (missing data = can't score)

  Lower-is-better (debt_to_earnings):
    value <= excellent        → 100
    (excellent, good]         → 75-100 (interpolated)
    (good, fair]              → 25-75  (interpolated)   ← was wrong: 50-75
    (fair, fair*2]            → 0-25   (interpolated)   ← was wrong: 0-50 with cap=10
    >= fair * 2               → 0
    NaN                       → 100 (no debt = excellent for Buffett)
"""

import sys
import os
import math
import pandas as pd
import pytest


# sys.path handled by conftest.py

from scoring.batch import BatchScoringMixin
from scoring.evaluator import StockEvaluator
from characters.config import Threshold

EXCELLENT = 20.0
GOOD = 15.0
FAIR = 10.0

DE_EXCELLENT = 2.0
DE_GOOD = 4.0
DE_FAIR = 7.0

GM_EXCELLENT = 50.0
GM_GOOD = 40.0
GM_FAIR = 30.0


# ── Minimal concrete subclass (no DB needed) ───────────────────────────────

class MinimalScorer(BatchScoringMixin):
    pass


scorer = MinimalScorer()


# ── Helpers ─────────────────────────────────────────────────────────────────

def roe_vec(value):
    """Score a single ROE value through the vectorized path."""
    s = pd.Series([value] if value is not None else [float('nan')])
    return scorer._vectorized_roe_score(s, EXCELLENT, GOOD, FAIR).iloc[0]


def gm_vec(value):
    """Score a single gross_margin value through the vectorized path."""
    s = pd.Series([value] if value is not None else [float('nan')])
    return scorer._vectorized_gross_margin_score(s, GM_EXCELLENT, GM_GOOD, GM_FAIR).iloc[0]


def de_vec(value):
    """Score a single debt_to_earnings value through the vectorized path."""
    s = pd.Series([value] if value is not None else [float('nan')])
    return scorer._vectorized_debt_earnings_score(s, DE_EXCELLENT, DE_GOOD, DE_FAIR).iloc[0]


# Reference scalar implementations taken directly from StockEvaluator
def roe_scalar(value):
    t = Threshold(excellent=EXCELLENT, good=GOOD, fair=FAIR, lower_is_better=False)
    if value is None or math.isnan(value):
        return 0.0  # StockEvaluator: missing ROE → 0
    return StockEvaluator._score_higher_is_better(None, value, t)


def gm_scalar(value):
    t = Threshold(excellent=GM_EXCELLENT, good=GM_GOOD, fair=GM_FAIR, lower_is_better=False)
    if value is None or math.isnan(value):
        return 0.0  # StockEvaluator: missing gross_margin → 0
    return StockEvaluator._score_higher_is_better(None, value, t)


def de_scalar(value):
    t = Threshold(excellent=DE_EXCELLENT, good=DE_GOOD, fair=DE_FAIR, lower_is_better=True)
    if value is None or math.isnan(value):
        return 100.0  # StockEvaluator: missing debt_to_earnings → 100 (no debt = good)
    return StockEvaluator._score_lower_is_better(None, value, t)


TOLERANCE = 0.1  # Allow up to 0.1 rounding difference


def approx_eq(a, b):
    return abs(a - b) <= TOLERANCE


# ══════════════════════════════════════════════════════════════════════════════
# ROE (higher is better)
# ══════════════════════════════════════════════════════════════════════════════

class TestRoeScoring:

    def test_roe_excellent_boundary(self):
        """ROE exactly at excellent threshold → 100."""
        assert roe_vec(EXCELLENT) == 100.0

    def test_roe_above_excellent(self):
        """ROE well above excellent → 100."""
        assert roe_vec(30.0) == 100.0

    def test_roe_midpoint_good_range(self):
        """ROE midpoint of [good, excellent) → 87.5."""
        mid = (GOOD + EXCELLENT) / 2  # 17.5
        expected = roe_scalar(mid)
        assert approx_eq(roe_vec(mid), expected), f"vec={roe_vec(mid):.2f} scalar={expected:.2f}"

    def test_roe_good_boundary(self):
        """ROE at good threshold → 75."""
        assert approx_eq(roe_vec(GOOD), 75.0)

    def test_roe_midpoint_fair_range(self):
        """ROE midpoint of [fair, good) → 50.0, NOT 62.5."""
        mid = (FAIR + GOOD) / 2  # 12.5
        expected = roe_scalar(mid)  # Should be 50.0
        result = roe_vec(mid)
        assert approx_eq(result, expected), (
            f"Fair range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Fair range should map to 25-75, not 50-75."
        )

    def test_roe_fair_boundary(self):
        """ROE at fair threshold → 25.0, NOT 50.0."""
        expected = roe_scalar(FAIR)  # Should be 25.0
        result = roe_vec(FAIR)
        assert approx_eq(result, expected), (
            f"Fair boundary: vec={result:.2f} expected={expected:.2f}. "
            f"ROE at fair should score 25, not 50."
        )

    def test_roe_midpoint_poor_range(self):
        """ROE midpoint of (0, fair) → 12.5, NOT 37.5."""
        mid = FAIR / 2  # 5.0
        expected = roe_scalar(mid)  # Should be 12.5
        result = roe_vec(mid)
        assert approx_eq(result, expected), (
            f"Poor range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Poor range should map to 0-25, not 25-50."
        )

    def test_roe_near_zero(self):
        """ROE near zero (positive) → close to 0."""
        result = roe_vec(0.1)
        assert result < 5.0, f"Near-zero ROE should score < 5, got {result:.2f}"

    def test_roe_zero(self):
        """ROE exactly 0 → 0."""
        assert roe_vec(0.0) == 0.0

    def test_roe_negative(self):
        """Negative ROE → 0."""
        assert roe_vec(-5.0) == 0.0

    def test_roe_missing(self):
        """Missing ROE → 0 (not 50)."""
        result = roe_vec(None)
        assert result == 0.0, f"Missing ROE should score 0, got {result:.2f}"

    def test_roe_matches_scalar_across_range(self):
        """Vectorized must match scalar for all meaningful ROE values."""
        test_values = [-10, 0, 1, 5, 10, 12.5, 15, 17.5, 20, 25, 30]
        for v in test_values:
            vec = roe_vec(v)
            scal = roe_scalar(v)
            assert approx_eq(vec, scal), f"ROE={v}: vec={vec:.2f} scalar={scal:.2f}"


# ══════════════════════════════════════════════════════════════════════════════
# Gross Margin (higher is better)
# ══════════════════════════════════════════════════════════════════════════════

class TestGrossMarginScoring:

    def test_gm_excellent_boundary(self):
        """Gross margin at excellent → 100."""
        assert gm_vec(GM_EXCELLENT) == 100.0

    def test_gm_above_excellent(self):
        """Gross margin above excellent → 100."""
        assert gm_vec(70.0) == 100.0

    def test_gm_midpoint_good_range(self):
        """Gross margin midpoint of [good, excellent) → 87.5."""
        mid = (GM_GOOD + GM_EXCELLENT) / 2  # 45.0
        expected = gm_scalar(mid)
        assert approx_eq(gm_vec(mid), expected)

    def test_gm_good_boundary(self):
        """Gross margin at good threshold → 75."""
        assert approx_eq(gm_vec(GM_GOOD), 75.0)

    def test_gm_midpoint_fair_range(self):
        """Gross margin midpoint of [fair, good) → 50.0, NOT 62.5."""
        mid = (GM_FAIR + GM_GOOD) / 2  # 35.0
        expected = gm_scalar(mid)  # Should be 50.0
        result = gm_vec(mid)
        assert approx_eq(result, expected), (
            f"Fair range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Fair range should map to 25-75, not 50-75."
        )

    def test_gm_fair_boundary(self):
        """Gross margin at fair threshold → 25.0, NOT 50.0."""
        expected = gm_scalar(GM_FAIR)
        result = gm_vec(GM_FAIR)
        assert approx_eq(result, expected), (
            f"Fair boundary: vec={result:.2f} expected={expected:.2f}"
        )

    def test_gm_midpoint_poor_range(self):
        """Gross margin midpoint of (0, fair) → 12.5, NOT 37.5."""
        mid = GM_FAIR / 2  # 15.0
        expected = gm_scalar(mid)  # Should be 12.5
        result = gm_vec(mid)
        assert approx_eq(result, expected), (
            f"Poor range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Poor range should map to 0-25, not 25-50."
        )

    def test_gm_zero(self):
        """Gross margin of 0 → 0."""
        assert gm_vec(0.0) == 0.0

    def test_gm_negative(self):
        """Negative gross margin → 0."""
        assert gm_vec(-10.0) == 0.0

    def test_gm_missing(self):
        """Missing gross margin → 0 (not 50)."""
        result = gm_vec(None)
        assert result == 0.0, f"Missing gross_margin should score 0, got {result:.2f}"

    def test_gm_matches_scalar_across_range(self):
        """Vectorized must match scalar for all meaningful gross margin values."""
        test_values = [-5, 0, 10, 15, 25, 30, 35, 40, 45, 50, 60]
        for v in test_values:
            vec = gm_vec(v)
            scal = gm_scalar(v)
            assert approx_eq(vec, scal), f"GM={v}: vec={vec:.2f} scalar={scal:.2f}"


# ══════════════════════════════════════════════════════════════════════════════
# Debt to Earnings (lower is better)
# ══════════════════════════════════════════════════════════════════════════════

class TestDebtToEarningsScoring:

    def test_de_excellent_boundary(self):
        """Debt/earnings at excellent threshold → 100."""
        assert de_vec(DE_EXCELLENT) == 100.0

    def test_de_below_excellent(self):
        """Debt/earnings below excellent → 100."""
        assert de_vec(0.5) == 100.0

    def test_de_midpoint_good_range(self):
        """Debt/earnings midpoint of (excellent, good] → 87.5."""
        mid = (DE_EXCELLENT + DE_GOOD) / 2  # 3.0
        expected = de_scalar(mid)
        assert approx_eq(de_vec(mid), expected)

    def test_de_good_boundary(self):
        """Debt/earnings at good threshold → 75."""
        assert approx_eq(de_vec(DE_GOOD), 75.0)

    def test_de_midpoint_fair_range(self):
        """Debt/earnings midpoint of (good, fair] → 50.0, NOT 62.5."""
        mid = (DE_GOOD + DE_FAIR) / 2  # 5.5
        expected = de_scalar(mid)  # Should be 50.0
        result = de_vec(mid)
        assert approx_eq(result, expected), (
            f"Fair range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Fair range should map to 25-75, not 50-75."
        )

    def test_de_fair_boundary(self):
        """Debt/earnings at fair threshold → 25.0, NOT 50.0."""
        expected = de_scalar(DE_FAIR)
        result = de_vec(DE_FAIR)
        assert approx_eq(result, expected), (
            f"Fair boundary: vec={result:.2f} expected={expected:.2f}"
        )

    def test_de_midpoint_poor_range(self):
        """Debt/earnings midpoint of (fair, fair*2) → 12.5, NOT variable based on hardcoded 10."""
        max_poor = DE_FAIR * 2  # 14.0
        mid = (DE_FAIR + max_poor) / 2  # 10.5
        expected = de_scalar(mid)  # Should be 12.5
        result = de_vec(mid)
        assert approx_eq(result, expected), (
            f"Poor range midpoint: vec={result:.2f} expected={expected:.2f}. "
            f"Poor range cap should be fair*2={max_poor}, not hardcoded 10."
        )

    def test_de_beyond_max(self):
        """Debt/earnings >= fair*2 → 0."""
        max_poor = DE_FAIR * 2  # 14.0
        assert de_vec(max_poor) == 0.0
        assert de_vec(20.0) == 0.0

    def test_de_between_old_cap_and_new_cap(self):
        """Value between old hardcoded cap (10) and new cap (fair*2=14) must score > 0."""
        # Old code: de=12 → 0 (since >= 10). Correct: de=12 → should be > 0 (still in poor range)
        result = de_vec(12.0)
        expected = de_scalar(12.0)
        assert approx_eq(result, expected), (
            f"de=12.0: vec={result:.2f} expected={expected:.2f}. "
            f"With fair=7, max_poor=14, de=12 should still score > 0."
        )
        assert result > 0.0, "de=12 should score > 0 (still within poor range)"

    def test_de_missing(self):
        """Missing debt/earnings → 100 (no debt = excellent for Buffett)."""
        result = de_vec(None)
        assert result == 100.0, f"Missing debt_to_earnings should score 100, got {result:.2f}"

    def test_de_matches_scalar_across_range(self):
        """Vectorized must match scalar for all meaningful D/E values."""
        test_values = [0, 1, 2, 3, 4, 5.5, 7, 8, 10.5, 14, 15, 20]
        for v in test_values:
            vec = de_vec(v)
            scal = de_scalar(v)
            assert approx_eq(vec, scal), f"D/E={v}: vec={vec:.2f} scalar={scal:.2f}"
