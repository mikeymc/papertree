# ABOUTME: Tests for BatchScoringMixin.evaluate_metrics() - single-stock vector scoring.
# ABOUTME: Validates that evaluate_metrics() produces the same scores as evaluate_batch().

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from lynch_criteria.batch import BatchScoringMixin


LYNCH_CONFIG = {
    'peg_excellent': 1.0,
    'peg_good': 1.5,
    'peg_fair': 2.0,
    'debt_excellent': 0.5,
    'debt_good': 1.0,
    'debt_moderate': 2.0,
    'inst_own_min': 0.20,
    'inst_own_max': 0.60,
    'weight_peg': 0.50,
    'weight_consistency': 0.25,
    'weight_debt': 0.15,
    'weight_ownership': 0.10,
}

# A full metrics dict as load_vectors() would produce
SAMPLE_METRICS = {
    'symbol': 'TEST',
    'company_name': 'Test Corp',
    'country': 'US',
    'sector': 'Technology',
    'ipo_year': 2010,
    'price': 100.0,
    'price_change_pct': 1.5,
    'market_cap': 1_000_000_000,
    'pe_ratio': 25.0,
    'peg_ratio': 1.2,
    'debt_to_equity': 0.3,
    'institutional_ownership': 0.45,
    'dividend_yield': 0.02,
    'earnings_cagr': 20.8,
    'revenue_cagr': 15.0,
    'income_consistency_score': 75.0,
    'revenue_consistency_score': 80.0,
    'pe_52_week_min': 20.0,
    'pe_52_week_max': 30.0,
    'pe_52_week_position': 50.0,
}


class ConcreteBatchScorer(BatchScoringMixin):
    """Minimal concrete class for testing the mixin without DB dependencies."""
    pass


@pytest.fixture
def scorer():
    return ConcreteBatchScorer()


def test_evaluate_metrics_returns_dict(scorer):
    result = scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)
    assert isinstance(result, dict)


def test_evaluate_metrics_includes_score(scorer):
    result = scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)
    assert 'overall_score' in result
    assert isinstance(result['overall_score'], float)
    assert 0 <= result['overall_score'] <= 100


def test_evaluate_metrics_includes_status(scorer):
    result = scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)
    assert 'overall_status' in result
    assert result['overall_status'] in ('STRONG_BUY', 'BUY', 'HOLD', 'CAUTION', 'AVOID')


def test_evaluate_metrics_preserves_symbol(scorer):
    result = scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)
    assert result['symbol'] == 'TEST'


def test_evaluate_metrics_matches_evaluate_batch(scorer):
    """evaluate_metrics should produce the same result as evaluate_batch on a 1-row DF."""
    import pandas as pd
    df = pd.DataFrame([SAMPLE_METRICS])
    batch_result = scorer.evaluate_batch(df, LYNCH_CONFIG).iloc[0].to_dict()
    single_result = scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)

    assert single_result['overall_score'] == batch_result['overall_score']
    assert single_result['overall_status'] == batch_result['overall_status']
    assert single_result['peg_score'] == batch_result['peg_score']
    assert single_result['debt_score'] == batch_result['debt_score']


def test_evaluate_metrics_handles_missing_optional_columns(scorer):
    """evaluate_metrics should work even when Buffett/PE-range columns are absent."""
    minimal = {
        'symbol': 'MIN',
        'peg_ratio': 1.5,
        'debt_to_equity': 0.8,
        'institutional_ownership': 0.35,
        'income_consistency_score': 60.0,
    }
    result = scorer.evaluate_metrics(minimal, LYNCH_CONFIG)
    assert result is not None
    assert 'overall_score' in result


def test_evaluate_metrics_accepts_consistency_score_alias(scorer):
    """evaluate_metrics should accept 'consistency_score' as alias for 'income_consistency_score'."""
    metrics = dict(SAMPLE_METRICS)
    del metrics['income_consistency_score']
    metrics['consistency_score'] = 75.0

    result = scorer.evaluate_metrics(metrics, LYNCH_CONFIG)
    assert result is not None
    assert result['overall_score'] == scorer.evaluate_metrics(SAMPLE_METRICS, LYNCH_CONFIG)['overall_score']


def test_evaluate_metrics_strong_buy_stock(scorer):
    """A stock with excellent metrics across all criteria should score STRONG_BUY."""
    excellent = dict(SAMPLE_METRICS)
    excellent['peg_ratio'] = 0.5      # Excellent PEG
    excellent['debt_to_equity'] = 0.1  # Excellent debt
    excellent['institutional_ownership'] = 0.40  # In sweet spot
    excellent['income_consistency_score'] = 90.0  # Very consistent

    result = scorer.evaluate_metrics(excellent, LYNCH_CONFIG)
    assert result['overall_score'] >= 80
    assert result['overall_status'] == 'STRONG_BUY'


def test_evaluate_metrics_avoid_stock(scorer):
    """A stock with poor metrics should score AVOID."""
    poor = dict(SAMPLE_METRICS)
    poor['peg_ratio'] = 5.0           # Very poor PEG
    poor['debt_to_equity'] = 6.0      # Very high debt
    poor['institutional_ownership'] = 0.0  # No institutional interest
    poor['income_consistency_score'] = 0.0  # No consistency

    result = scorer.evaluate_metrics(poor, LYNCH_CONFIG)
    assert result['overall_score'] < 40
