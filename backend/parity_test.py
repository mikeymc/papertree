# ABOUTME: Empirical parity test comparing scalar and vector scoring paths.
# ABOUTME: Scores the full stock universe through both engines and reports any divergence.
"""
Run with:  uv run python backend/parity_test.py

Loads all stocks from the DB, scores each through both the legacy scalar
evaluate_stock() path AND the vector evaluate_batch() path, then prints a
full divergence report.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from earnings_analyzer import EarningsAnalyzer
from lynch_criteria import LynchCriteria
from stock_vectors import StockVectors, DEFAULT_ALGORITHM_CONFIG
from characters.buffett import BUFFETT

SCORE_TOLERANCE = 0.5   # float rounding tolerance for scores
STATUS_EXACT = True     # statuses must match exactly


def run_parity(character: str):
    db = Database()
    analyzer = EarningsAnalyzer(db)
    criteria = LynchCriteria(db, analyzer)
    vectors = StockVectors(db)

    print(f"\n=== Parity test: {character.upper()} ===")

    # Build config for each character
    if character == 'lynch':
        config = DEFAULT_ALGORITHM_CONFIG.copy()
    elif character == 'buffett':
        # Mirrors the actual BUFFETT CharacterConfig weights and thresholds exactly.
        # 'weight_consistency' maps to income_consistency_score in evaluate_batch(),
        # which is the same value StockEvaluator uses as 'earnings_consistency'.
        config = {
            'weight_roe': 0.40,
            'weight_consistency': 0.30,
            'weight_debt_to_earnings': 0.20,
            'weight_gross_margin': 0.10,
            'weight_peg': 0.0,
            'weight_debt': 0.0,
            'weight_ownership': 0.0,
            'roe_excellent': 20.0, 'roe_good': 15.0, 'roe_fair': 10.0,
            'debt_to_earnings_excellent': 2.0, 'debt_to_earnings_good': 4.0, 'debt_to_earnings_fair': 7.0,
            'gross_margin_excellent': 50.0, 'gross_margin_good': 40.0, 'gross_margin_fair': 30.0,
            # StockEvaluator returns 0 for unknown consistency; match that default here
            'consistency_null_default': 0.0,
        }
    else:
        raise ValueError(f"Unknown character: {character}")

    # Load full vector universe
    print("Loading vector universe...")
    df = vectors.load_vectors()
    print(f"Loaded {len(df)} stocks")

    # Score all via vector path
    print("Scoring via vector path...")
    scored_df = criteria.evaluate_batch(df, config)
    vector_scores = {
        row['symbol']: {
            'overall_score': row['overall_score'],
            'overall_status': row['overall_status'],
        }
        for _, row in scored_df.iterrows()
    }

    # Score all via scalar path
    print("Scoring via scalar path...")
    scalar_scores = {}
    errors = []
    for symbol in list(vector_scores.keys()):
        try:
            result = criteria.evaluate_stock(symbol, character_id=character)
            if result:
                scalar_scores[symbol] = {
                    'overall_score': result['overall_score'],
                    'overall_status': result['overall_status'],
                }
        except Exception as e:
            errors.append((symbol, str(e)))

    print(f"Scored {len(scalar_scores)} stocks via scalar path ({len(errors)} errors)")

    # Compare
    mismatches = []
    score_only_diffs = []
    status_only_diffs = []
    exact_matches = 0

    for symbol, vec in vector_scores.items():
        scal = scalar_scores.get(symbol)
        if scal is None:
            continue

        score_diff = abs(vec['overall_score'] - scal['overall_score'])
        status_match = vec['overall_status'] == scal['overall_status']

        if score_diff <= SCORE_TOLERANCE and status_match:
            exact_matches += 1
        elif score_diff > SCORE_TOLERANCE and not status_match:
            mismatches.append({
                'symbol': symbol,
                'vec_score': vec['overall_score'],
                'scal_score': scal['overall_score'],
                'score_diff': round(score_diff, 1),
                'vec_status': vec['overall_status'],
                'scal_status': scal['overall_status'],
            })
        elif score_diff > SCORE_TOLERANCE:
            score_only_diffs.append({
                'symbol': symbol,
                'vec_score': vec['overall_score'],
                'scal_score': scal['overall_score'],
                'score_diff': round(score_diff, 1),
                'status': vec['overall_status'],
            })
        else:
            status_only_diffs.append({
                'symbol': symbol,
                'score': vec['overall_score'],
                'vec_status': vec['overall_status'],
                'scal_status': scal['overall_status'],
            })

    total_compared = exact_matches + len(mismatches) + len(score_only_diffs) + len(status_only_diffs)
    print(f"\nResults for {len(total_compared and [1] or [])} ({total_compared}) stocks compared:")
    print(f"  Exact matches (within {SCORE_TOLERANCE} pts + same status): {exact_matches}")
    print(f"  Score + status both differ:                                 {len(mismatches)}")
    print(f"  Score differs (same status):                                {len(score_only_diffs)}")
    print(f"  Status differs (same score):                                {len(status_only_diffs)}")

    if mismatches:
        print(f"\nTop 20 full mismatches (sorted by score diff):")
        for m in sorted(mismatches, key=lambda x: -x['score_diff'])[:20]:
            print(f"  {m['symbol']:8s}  vec={m['vec_score']:5.1f} ({m['vec_status']:10s})  "
                  f"scal={m['scal_score']:5.1f} ({m['scal_status']:10s})  diff={m['score_diff']:5.1f}")

    if score_only_diffs:
        print(f"\nTop 20 score-only diffs:")
        for m in sorted(score_only_diffs, key=lambda x: -x['score_diff'])[:20]:
            print(f"  {m['symbol']:8s}  vec={m['vec_score']:5.1f}  scal={m['scal_score']:5.1f}  "
                  f"diff={m['score_diff']:5.1f}  status={m['status']}")

    if status_only_diffs:
        print(f"\nTop 20 status-only diffs:")
        for m in sorted(status_only_diffs, key=lambda x: x['score'])[:20]:
            print(f"  {m['symbol']:8s}  score={m['score']:5.1f}  vec={m['vec_status']:10s}  scal={m['scal_status']}")

    if errors:
        print(f"\nErrors during scalar scoring ({len(errors)}):")
        for sym, err in errors[:10]:
            print(f"  {sym}: {err}")

    return {
        'exact': exact_matches,
        'mismatches': len(mismatches),
        'score_diffs': len(score_only_diffs),
        'status_diffs': len(status_only_diffs),
        'errors': len(errors),
        'total': total_compared,
    }


if __name__ == '__main__':
    lynch_result = run_parity('lynch')
    buffett_result = run_parity('buffett')

    print("\n=== SUMMARY ===")
    for char, r in [('lynch', lynch_result), ('buffett', buffett_result)]:
        pct_exact = 100 * r['exact'] / r['total'] if r['total'] else 0
        print(f"{char:8s}: {r['total']} compared, {r['exact']} exact ({pct_exact:.1f}%), "
              f"{r['mismatches']} full mismatches, {r['score_diffs']} score-only, "
              f"{r['status_diffs']} status-only, {r['errors']} errors")
