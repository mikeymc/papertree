# ABOUTME: Tests verifying stock_rescorer and strategy_executor use vector scoring
# ABOUTME: Ensures evaluate_stock() scalar path is no longer called in these components

import sys
import os
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from stock_rescorer import StockRescorer
from strategy_executor.core import StrategyExecutorCore


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_scored_df(symbols, overall_score=75.0, overall_status='PASS'):
    return pd.DataFrame([{
        'symbol': s,
        'overall_score': overall_score,
        'overall_status': overall_status,
        'peg_score': 80.0,
        'debt_score': 70.0,
        'institutional_ownership_score': 65.0,
    } for s in symbols])


def _make_vector_df(symbols):
    return pd.DataFrame([{
        'symbol': s,
        'peg_ratio': 1.5,
        'debt_to_equity': 0.5,
        'institutional_ownership': 0.6,
    } for s in symbols])


# ══════════════════════════════════════════════════════════════════════════════
# StockRescorer
# ══════════════════════════════════════════════════════════════════════════════

class TestStockRescorerUsesVectorPath:

    def _build_rescorer(self):
        mock_db = MagicMock()
        mock_criteria = MagicMock()
        return StockRescorer(mock_db, mock_criteria), mock_db, mock_criteria

    def test_rescore_calls_evaluate_batch_not_evaluate_stock(self):
        """rescore_saved_stocks must use evaluate_batch, never evaluate_stock."""
        rescorer, mock_db, mock_criteria = self._build_rescorer()

        symbols = ['AAPL', 'MSFT', 'GOOGL']
        mock_db.get_latest_session.return_value = {'session_id': 42}
        mock_db.get_screening_symbols.return_value = symbols
        mock_criteria.evaluate_batch.return_value = _make_scored_df(symbols)

        with patch('stock_rescorer.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df(symbols)

            rescorer.rescore_saved_stocks()

        mock_criteria.evaluate_batch.assert_called_once()
        mock_criteria.evaluate_stock.assert_not_called()

    def test_rescore_updates_db_with_batch_scores(self):
        """DB update must use scores from evaluate_batch output."""
        rescorer, mock_db, mock_criteria = self._build_rescorer()

        symbols = ['AAPL']
        mock_db.get_latest_session.return_value = {'session_id': 1}
        mock_db.get_screening_symbols.return_value = symbols
        mock_criteria.evaluate_batch.return_value = _make_scored_df(
            symbols, overall_score=88.5, overall_status='PASS'
        )

        with patch('stock_rescorer.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df(symbols)

            rescorer.rescore_saved_stocks()

        mock_db.update_screening_result_scores.assert_called_once()
        kwargs = mock_db.update_screening_result_scores.call_args[1]
        assert kwargs['symbol'] == 'AAPL'
        assert kwargs['overall_score'] == 88.5
        assert kwargs['overall_status'] == 'PASS'

    def test_rescore_returns_success_count(self):
        """rescore_saved_stocks must return summary with correct success count."""
        rescorer, mock_db, mock_criteria = self._build_rescorer()

        symbols = ['AAPL', 'MSFT']
        mock_db.get_latest_session.return_value = {'session_id': 1}
        mock_db.get_screening_symbols.return_value = symbols
        mock_criteria.evaluate_batch.return_value = _make_scored_df(symbols)

        with patch('stock_rescorer.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df(symbols)

            summary = rescorer.rescore_saved_stocks()

        assert summary['success'] == 2
        assert summary['total'] == 2
        assert summary['failed'] == 0

    def test_rescore_no_session_returns_empty_summary(self):
        """Returns zero-count summary when no screening session exists."""
        rescorer, mock_db, mock_criteria = self._build_rescorer()
        mock_db.get_latest_session.return_value = None

        summary = rescorer.rescore_saved_stocks()

        assert summary['total'] == 0
        mock_criteria.evaluate_batch.assert_not_called()
        mock_criteria.evaluate_stock.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# StrategyExecutorCore._get_current_scores
# ══════════════════════════════════════════════════════════════════════════════

class TestGetCurrentScoresUsesVectorPath:

    def _build_executor(self):
        mock_db = MagicMock()
        mock_criteria = MagicMock()
        executor = StrategyExecutorCore.__new__(StrategyExecutorCore)
        executor.db = mock_db
        executor._lynch_criteria = mock_criteria  # backing attr for the property
        executor.universe_filter = MagicMock()
        executor.consensus_engine = MagicMock()
        executor.position_sizer = MagicMock()
        executor.exit_checker = MagicMock()
        executor.benchmark_tracker = MagicMock()
        return executor, mock_db, mock_criteria

    def _make_scored_single(self, lynch_score=72.0, buffett_score=65.0):
        """Build paired DataFrames for Lynch + Buffett single-symbol scoring."""
        lynch_df = pd.DataFrame([{
            'symbol': 'AAPL',
            'overall_score': lynch_score,
            'overall_status': 'PASS',
        }])
        buffett_df = pd.DataFrame([{
            'symbol': 'AAPL',
            'overall_score': buffett_score,
            'overall_status': 'CLOSE',
        }])
        return lynch_df, buffett_df

    def test_get_current_scores_uses_evaluate_batch(self):
        """_get_current_scores must call evaluate_batch, never evaluate_stock."""
        executor, mock_db, mock_criteria = self._build_executor()

        lynch_df, buffett_df = self._make_scored_single()
        mock_criteria.evaluate_batch.side_effect = [lynch_df, buffett_df]

        with patch('strategy_executor.core.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df(['AAPL'])

            scores = executor._get_current_scores('AAPL')

        assert mock_criteria.evaluate_batch.call_count == 2
        mock_criteria.evaluate_stock.assert_not_called()

    def test_get_current_scores_returns_both_characters(self):
        """Result must contain lynch_score, lynch_status, buffett_score, buffett_status."""
        executor, mock_db, mock_criteria = self._build_executor()

        lynch_df, buffett_df = self._make_scored_single(lynch_score=72.0, buffett_score=65.0)
        mock_criteria.evaluate_batch.side_effect = [lynch_df, buffett_df]

        with patch('strategy_executor.core.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df(['AAPL'])

            scores = executor._get_current_scores('AAPL')

        assert scores['lynch_score'] == 72.0
        assert scores['lynch_status'] == 'PASS'
        assert scores['buffett_score'] == 65.0
        assert scores['buffett_status'] == 'CLOSE'

    def test_get_current_scores_returns_empty_for_unknown_symbol(self):
        """Returns empty dict when symbol is not in vector universe."""
        executor, mock_db, mock_criteria = self._build_executor()

        with patch('strategy_executor.core.StockVectors') as mock_sv_class:
            mock_sv = MagicMock()
            mock_sv_class.return_value = mock_sv
            mock_sv.load_vectors.return_value = _make_vector_df([])  # empty

            scores = executor._get_current_scores('UNKN')

        assert scores == {}
        mock_criteria.evaluate_batch.assert_not_called()
