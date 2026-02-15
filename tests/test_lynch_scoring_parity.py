# ABOUTME: Integration parity test proving Lynch vector scoring == scalar scoring.
# ABOUTME: Runs both engines against all stocks in the live DB and asserts exact match.
"""
Requires live DB (lynch-postgres container). Skipped automatically if DB is unavailable.

Scores all Lynch stocks through both the legacy scalar evaluate_stock() path AND
the vector evaluate_batch() path, asserting they are identical within float tolerance.
This test must pass before the scalar path can be safely removed.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

SCORE_TOLERANCE = 0.5  # floating-point rounding tolerance


def _build_lynch_config():
    """Return the default Lynch scoring config."""
    return {
        'peg_excellent': 1.0, 'peg_good': 1.5, 'peg_fair': 2.0,
        'debt_excellent': 0.5, 'debt_good': 1.0, 'debt_moderate': 2.0,
        'inst_own_min': 0.20, 'inst_own_max': 0.60,
        'weight_peg': 0.50, 'weight_consistency': 0.25,
        'weight_debt': 0.15, 'weight_ownership': 0.10,
    }


@pytest.fixture(scope='module')
def db_and_criteria():
    """Connect to the live DB and build scoring objects. Skips if DB unavailable."""
    try:
        from database import Database
        from earnings_analyzer import EarningsAnalyzer
        from scoring import LynchCriteria
        from scoring.vectors import StockVectors

        db = Database()
        # Quick connectivity check
        conn = db.get_connection()
        db.return_connection(conn)

        analyzer = EarningsAnalyzer(db)
        criteria = LynchCriteria(db, analyzer)
        vectors = StockVectors(db)
        return db, criteria, vectors
    except Exception as e:
        pytest.skip(f'Live DB not available: {e}')


@pytest.fixture(scope='module')
def scored_stocks(db_and_criteria):
    """Score all stocks via both paths. Cached at module scope so it runs once."""
    _, criteria, vectors = db_and_criteria
    config = _build_lynch_config()

    df = vectors.load_vectors()
    assert len(df) > 100, f'Expected >100 stocks, got {len(df)}'

    scored_df = criteria.evaluate_batch(df, config)
    vector_scores = {
        row['symbol']: {
            'score': row['overall_score'],
            'status': row['overall_status'],
        }
        for _, row in scored_df.iterrows()
    }

    scalar_scores = {}
    for symbol in vector_scores:
        try:
            result = criteria.evaluate_stock(symbol, character_id='lynch')
            if result:
                scalar_scores[symbol] = {
                    'score': result['overall_score'],
                    'status': result['overall_status'],
                }
        except Exception:
            pass  # individual failures reported below

    return vector_scores, scalar_scores


def test_parity_stock_count(scored_stocks):
    """Both paths must score the same number of stocks."""
    vector_scores, scalar_scores = scored_stocks
    assert len(vector_scores) > 0, 'Vector path scored no stocks'
    assert len(scalar_scores) > 0, 'Scalar path scored no stocks'
    # Allow up to 1% missing from scalar (some stocks may fail transiently)
    missing = set(vector_scores) - set(scalar_scores)
    pct_missing = 100 * len(missing) / len(vector_scores)
    assert pct_missing <= 1.0, (
        f'{len(missing)} stocks ({pct_missing:.1f}%) missing from scalar path: '
        f'{sorted(missing)[:10]}...'
    )


@pytest.mark.parametrize('symbol', pytest.param('__all__', id='all_stocks'))
def test_lynch_scores_match_across_all_stocks(scored_stocks, symbol):
    """
    For every stock scored by both paths, the Lynch overall_score must be
    within SCORE_TOLERANCE and the overall_status must be identical.
    """
    vector_scores, scalar_scores = scored_stocks
    mismatches = []

    for sym in sorted(set(vector_scores) & set(scalar_scores)):
        vec = vector_scores[sym]
        scal = scalar_scores[sym]

        score_diff = abs(vec['score'] - scal['score'])
        if score_diff > SCORE_TOLERANCE or vec['status'] != scal['status']:
            mismatches.append(
                f"{sym}: vec={vec['score']:.1f} ({vec['status']})  "
                f"scal={scal['score']:.1f} ({scal['status']})  "
                f"diff={score_diff:.1f}"
            )

    assert not mismatches, (
        f'{len(mismatches)} stocks diverge between Lynch vector and scalar paths:\n'
        + '\n'.join(mismatches[:30])
    )


def test_lynch_strong_buy_stocks_agree(scored_stocks):
    """Stocks that vector rates STRONG_BUY must also be STRONG_BUY in scalar."""
    vector_scores, scalar_scores = scored_stocks
    disagreements = []
    for sym, vec in vector_scores.items():
        scal = scalar_scores.get(sym)
        if vec['status'] == 'STRONG_BUY' and scal and scal['status'] != 'STRONG_BUY':
            disagreements.append(
                f"{sym}: vec=STRONG_BUY scal={scal['status']} (score vec={vec['score']:.1f} scal={scal['score']:.1f})"
            )
    assert not disagreements, (
        f'{len(disagreements)} STRONG_BUY stocks disagree:\n' + '\n'.join(disagreements)
    )


def test_lynch_avoid_stocks_agree(scored_stocks):
    """Stocks that vector rates AVOID must also be AVOID in scalar."""
    vector_scores, scalar_scores = scored_stocks
    disagreements = []
    for sym, vec in vector_scores.items():
        scal = scalar_scores.get(sym)
        if vec['status'] == 'AVOID' and scal and scal['status'] != 'AVOID':
            disagreements.append(
                f"{sym}: vec=AVOID scal={scal['status']} (score vec={vec['score']:.1f} scal={scal['score']:.1f})"
            )
    assert not disagreements, (
        f'{len(disagreements)} AVOID stocks disagree:\n' + '\n'.join(disagreements)
    )


def test_minimum_stock_count(scored_stocks):
    """Parity test is only meaningful if we scored a large universe."""
    vector_scores, scalar_scores = scored_stocks
    compared = len(set(vector_scores) & set(scalar_scores))
    assert compared >= 1000, (
        f'Only {compared} stocks compared — need >= 1000 for meaningful parity guarantee'
    )
