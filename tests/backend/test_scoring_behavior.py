# ABOUTME: BDD-style tests for the scoring mixin's candidate evaluation logic
# ABOUTME: Covers OR logic, threshold calculation, new-vs-addition behavior, and held stock routing

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch

from strategy_executor.scoring import ScoringMixin


class ScoringHarness(ScoringMixin):
    """Minimal harness providing just enough context for ScoringMixin methods."""

    def __init__(self, db=None, lynch_criteria=None):
        self.db = db or Mock()
        self._lynch_criteria = lynch_criteria

    @property
    def lynch_criteria(self):
        return self._lynch_criteria


def make_scored_df(rows):
    """Build a DataFrame matching _calculate_batch_scores output.

    Each row is a dict with at least 'symbol'. Missing score/status keys
    are filled with defaults (score=0, status='N/A').
    """
    defaults = {
        'lynch_score': 0.0, 'lynch_status': 'N/A',
        'buffett_score': 0.0, 'buffett_status': 'N/A',
    }
    return pd.DataFrame([{**defaults, **r} for r in rows])


# ═══════════════════════════════════════════════════════════════════════
# OR Logic: A stock passes if ANY analyst meets its threshold
# ═══════════════════════════════════════════════════════════════════════

class TestCandidatePassesWhenAnyAnalystMeetsThreshold:

    @pytest.fixture
    def scorer(self):
        return ScoringHarness()

    def test_passes_when_both_analysts_meet_threshold(self, scorer):
        """Given both Lynch and Buffett score above threshold,
        when evaluated, then the stock passes."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 75, 'lynch_status': 'BUY',
             'buffett_score': 80, 'buffett_status': 'STRONG_BUY'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 1
        assert passed[0]['symbol'] == 'AAPL'

    def test_passes_when_only_lynch_meets_threshold(self, scorer):
        """Given Lynch scores above threshold but Buffett does not,
        when evaluated, then the stock still passes (OR logic)."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 75, 'lynch_status': 'BUY',
             'buffett_score': 40, 'buffett_status': 'CAUTION'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 1
        assert passed[0]['symbol'] == 'AAPL'

    def test_passes_when_only_buffett_meets_threshold(self, scorer):
        """Given Buffett scores above threshold but Lynch does not,
        when evaluated, then the stock still passes (OR logic)."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 40, 'lynch_status': 'CAUTION',
             'buffett_score': 75, 'buffett_status': 'BUY'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 1
        assert passed[0]['symbol'] == 'AAPL'

    def test_fails_when_no_analyst_meets_threshold(self, scorer):
        """Given neither analyst scores above threshold,
        when evaluated as new position, then the stock fails
        and declined is empty (declined only populated for additions)."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 50, 'lynch_status': 'HOLD',
             'buffett_score': 55, 'buffett_status': 'HOLD'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 0
        assert len(declined) == 0

    def test_passes_at_exact_threshold_boundary(self, scorer):
        """Given one analyst scores exactly at threshold (>=),
        when evaluated, then the stock passes."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 60, 'lynch_status': 'BUY',
             'buffett_score': 30, 'buffett_status': 'AVOID'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, _ = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 1

    def test_multiple_stocks_evaluated_independently(self, scorer):
        """Given three stocks with different score profiles,
        when evaluated, then each is judged independently."""
        df = make_scored_df([
            # Both pass
            {'symbol': 'AAPL', 'lynch_score': 80, 'lynch_status': 'BUY',
             'buffett_score': 70, 'buffett_status': 'BUY'},
            # Only Buffett passes
            {'symbol': 'MSFT', 'lynch_score': 40, 'lynch_status': 'CAUTION',
             'buffett_score': 65, 'buffett_status': 'BUY'},
            # Neither passes
            {'symbol': 'GOOGL', 'lynch_score': 50, 'lynch_status': 'HOLD',
             'buffett_score': 55, 'buffett_status': 'HOLD'},
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, _ = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        symbols = [s['symbol'] for s in passed]
        assert 'AAPL' in symbols
        assert 'MSFT' in symbols
        assert 'GOOGL' not in symbols


# ═══════════════════════════════════════════════════════════════════════
# Single analyst mode: only the active analyst's score matters
# ═══════════════════════════════════════════════════════════════════════

class TestSingleAnalystScoring:

    @pytest.fixture
    def scorer(self):
        return ScoringHarness()

    def test_lynch_only_ignores_buffett_score(self, scorer):
        """Given only Lynch is active,
        when Buffett would have failed, the stock still passes on Lynch alone."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 75, 'lynch_status': 'BUY'}
        ])
        thresholds = {'lynch': 60}

        passed, _ = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch'])

        assert len(passed) == 1
        # Buffett score should be zeroed out since not active
        assert passed[0]['buffett_score'] == 0
        assert passed[0]['buffett_status'] == 'N/A'

    def test_buffett_only_ignores_lynch_score(self, scorer):
        """Given only Buffett is active,
        when Lynch would have failed, the stock still passes on Buffett alone."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'buffett_score': 75, 'buffett_status': 'BUY'}
        ])
        thresholds = {'buffett': 60}

        passed, _ = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['buffett'])

        assert len(passed) == 1
        assert passed[0]['lynch_score'] == 0
        assert passed[0]['lynch_status'] == 'N/A'


# ═══════════════════════════════════════════════════════════════════════
# Threshold calculation: new positions vs additions
# ═══════════════════════════════════════════════════════════════════════

class TestScoringThresholds:

    @pytest.fixture
    def scorer(self):
        return ScoringHarness()

    def test_new_position_uses_base_thresholds(self, scorer):
        """Given scoring_requirements with min_score 60/65,
        when getting thresholds for a new position,
        then those exact thresholds are returned."""
        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
                {'character': 'buffett', 'min_score': 65},
            ]
        }

        thresholds = scorer._get_scoring_thresholds(
            conditions, is_addition=False, analysts=['lynch', 'buffett'])

        assert thresholds == {'lynch': 60, 'buffett': 65}

    def test_addition_defaults_to_base_plus_ten(self, scorer):
        """Given no explicit addition_scoring_requirements,
        when getting thresholds for an addition,
        then base thresholds + 10 are used."""
        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
                {'character': 'buffett', 'min_score': 65},
            ]
        }

        thresholds = scorer._get_scoring_thresholds(
            conditions, is_addition=True, analysts=['lynch', 'buffett'])

        assert thresholds == {'lynch': 70, 'buffett': 75}

    def test_addition_uses_explicit_requirements_when_provided(self, scorer):
        """Given explicit addition_scoring_requirements,
        when getting thresholds for an addition,
        then those explicit thresholds override the +10 default."""
        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
                {'character': 'buffett', 'min_score': 60},
            ],
            'addition_scoring_requirements': [
                {'character': 'lynch', 'min_score': 80},
                {'character': 'buffett', 'min_score': 85},
            ]
        }

        thresholds = scorer._get_scoring_thresholds(
            conditions, is_addition=True, analysts=['lynch', 'buffett'])

        assert thresholds == {'lynch': 80, 'buffett': 85}

    def test_missing_scoring_requirements_uses_default_60(self, scorer):
        """Given no scoring_requirements in conditions,
        when getting thresholds, then default of 60 (SCORE_THRESHOLDS['BUY']) is used."""
        conditions = {}

        thresholds = scorer._get_scoring_thresholds(
            conditions, is_addition=False, analysts=['lynch', 'buffett'])

        assert thresholds == {'lynch': 60, 'buffett': 60}

    def test_addition_with_no_base_reqs_uses_default_plus_ten(self, scorer):
        """Given no scoring_requirements and no addition_scoring_requirements,
        when getting addition thresholds, then 60 + 10 = 70 is used."""
        conditions = {}

        thresholds = scorer._get_scoring_thresholds(
            conditions, is_addition=True, analysts=['lynch', 'buffett'])

        assert thresholds == {'lynch': 70, 'buffett': 70}


# ═══════════════════════════════════════════════════════════════════════
# Held stock routing: failing additions go to declined for deliberation
# ═══════════════════════════════════════════════════════════════════════

class TestFailingHeldStocksRouteToDeliberation:

    @pytest.fixture
    def scorer(self):
        return ScoringHarness()

    def test_failing_addition_goes_to_declined_list(self, scorer):
        """Given a held stock that fails addition thresholds,
        when evaluated as addition,
        then it appears in declined (not passed) for deliberation routing."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 55, 'lynch_status': 'HOLD',
             'buffett_score': 50, 'buffett_status': 'HOLD'}
        ])
        thresholds = {'lynch': 70, 'buffett': 70}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=True, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 0
        assert len(declined) == 1
        assert declined[0]['symbol'] == 'AAPL'

    def test_declined_stock_gets_exit_evaluation_position_type(self, scorer):
        """Given a held stock that fails addition thresholds,
        when declined, then its position_type is set to 'held_exit_evaluation'
        so downstream phases know to evaluate it for exit."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 55, 'lynch_status': 'HOLD',
             'buffett_score': 50, 'buffett_status': 'HOLD'}
        ])
        thresholds = {'lynch': 70, 'buffett': 70}

        _, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=True, run_id=1, analysts=['lynch', 'buffett'])

        assert declined[0]['position_type'] == 'held_exit_evaluation'

    def test_failing_new_position_does_not_go_to_declined(self, scorer):
        """Given a new stock that fails thresholds,
        when evaluated as new (not addition),
        then declined is empty — only additions get routed to deliberation."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 40, 'lynch_status': 'CAUTION',
             'buffett_score': 35, 'buffett_status': 'AVOID'}
        ])
        thresholds = {'lynch': 60, 'buffett': 60}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=False, run_id=1, analysts=['lynch', 'buffett'])

        assert len(passed) == 0
        assert len(declined) == 0

    def test_mixed_pass_and_decline_among_held_stocks(self, scorer):
        """Given two held stocks — one passes addition threshold, one fails —
        when evaluated as additions,
        then passing goes to scored, failing goes to declined."""
        df = make_scored_df([
            {'symbol': 'AAPL', 'lynch_score': 80, 'lynch_status': 'STRONG_BUY',
             'buffett_score': 75, 'buffett_status': 'BUY'},
            {'symbol': 'MSFT', 'lynch_score': 55, 'lynch_status': 'HOLD',
             'buffett_score': 50, 'buffett_status': 'HOLD'},
        ])
        thresholds = {'lynch': 70, 'buffett': 70}

        passed, declined = scorer._evaluate_candidates(
            df, thresholds, is_addition=True, run_id=1, analysts=['lynch', 'buffett'])

        assert [s['symbol'] for s in passed] == ['AAPL']
        assert [s['symbol'] for s in declined] == ['MSFT']
        assert passed[0]['position_type'] == 'addition'
        assert declined[0]['position_type'] == 'held_exit_evaluation'


# ═══════════════════════════════════════════════════════════════════════
# Full _score_candidates flow with mocked boundaries
# ═══════════════════════════════════════════════════════════════════════

class TestScoreCandidatesEndToEnd:
    """Tests the full _score_candidates method, mocking only external
    boundaries (StockVectors for DB access, evaluate_batch for scoring engine)."""

    def _make_vectors_mock(self, symbols_and_data):
        """Create a StockVectors mock that returns a DataFrame for the given symbols."""
        rows = []
        for sym in symbols_and_data:
            rows.append({
                'symbol': sym, 'price': 100.0, 'peg_ratio': 1.5,
                'debt_to_equity': 0.5, 'institutional_ownership': 0.6,
            })
        df = pd.DataFrame(rows)
        mock_class = MagicMock()
        mock_class.return_value.load_vectors.return_value = df
        return mock_class

    def _make_evaluate_batch(self, score_map):
        """Create an evaluate_batch side_effect that assigns scores per symbol.

        score_map: {symbol: (score, status)}
        """
        def evaluate_batch(df, config):
            result = df[['symbol']].copy()
            result['overall_score'] = result['symbol'].map(
                lambda s: score_map.get(s, (0, 'N/A'))[0])
            result['overall_status'] = result['symbol'].map(
                lambda s: score_map.get(s, (0, 'N/A'))[1])
            return result
        return evaluate_batch

    def test_stock_passing_one_analyst_flows_through(self):
        """Given AAPL scores 75 on Lynch but 40 on Buffett,
        when scored as new candidate with threshold 60,
        then AAPL passes (OR logic) with correct scores attached."""
        mock_lynch = Mock()
        mock_lynch.evaluate_batch = Mock(side_effect=self._make_evaluate_batch({
            'AAPL': (75, 'BUY'),
        }))

        scorer = ScoringHarness(lynch_criteria=mock_lynch)
        scorer.db.append_to_run_log = Mock()

        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
                {'character': 'buffett', 'min_score': 60},
            ]
        }

        with patch('scoring.vectors.StockVectors', self._make_vectors_mock(['AAPL'])):
            passed, declined = scorer._score_candidates(
                candidates=['AAPL'], conditions=conditions, run_id=1,
                is_addition=False, analysts=['lynch', 'buffett'])

        assert len(passed) == 1
        assert passed[0]['symbol'] == 'AAPL'
        assert passed[0]['lynch_score'] == 75
        assert passed[0]['position_type'] == 'new'

    def test_empty_candidates_returns_empty(self):
        """Given no candidates, when scored, then returns empty lists immediately."""
        scorer = ScoringHarness()

        passed, declined = scorer._score_candidates(
            candidates=[], conditions={}, run_id=1)

        assert passed == []
        assert declined == []

    def test_addition_applies_higher_threshold(self):
        """Given AAPL scores 65 on Lynch,
        when scored as new (threshold 60) it passes,
        but when scored as addition (threshold 70) it fails and goes to declined."""
        mock_lynch = Mock()
        mock_lynch.evaluate_batch = Mock(side_effect=self._make_evaluate_batch({
            'AAPL': (65, 'BUY'),
        }))

        scorer = ScoringHarness(lynch_criteria=mock_lynch)
        scorer.db.append_to_run_log = Mock()

        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
            ]
        }

        # As new position: 65 >= 60 → passes
        with patch('scoring.vectors.StockVectors', self._make_vectors_mock(['AAPL'])):
            passed_new, _ = scorer._score_candidates(
                candidates=['AAPL'], conditions=conditions, run_id=1,
                is_addition=False, analysts=['lynch'])

        assert len(passed_new) == 1

        # As addition: 65 < 70 (60+10) → fails, goes to declined
        with patch('scoring.vectors.StockVectors', self._make_vectors_mock(['AAPL'])):
            passed_add, declined_add = scorer._score_candidates(
                candidates=['AAPL'], conditions=conditions, run_id=1,
                is_addition=True, analysts=['lynch'])

        assert len(passed_add) == 0
        assert len(declined_add) == 1
        assert declined_add[0]['position_type'] == 'held_exit_evaluation'
