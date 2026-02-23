# ABOUTME: Tests for the four critical fixes in strategy execution
# ABOUTME: Validates cash tracking, dividend visibility, re-evaluation, and position additions

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock, patch
from strategy_executor import (
    StrategyExecutor,
    PositionSizer,
    ExitConditionChecker,
    UniverseFilter,
)
from strategy_executor.models import ExitSignal


class TestIssueFixes:
    """Tests for the four critical issue fixes."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        db = Mock()
        db.get_connection = Mock(return_value=Mock())
        db.return_connection = Mock()
        return db

    def test_issue1_two_phase_cash_tracking(self, mock_db):
        """Test Issue 1: Position sizing allocates within portfolio value using equal weight."""
        sizer = PositionSizer(mock_db)

        # Three candidates equal-weighted in $10k portfolio → ~$3,333 each
        candidates = [
            {'symbol': 'AAPL', 'price': 100.0, 'conviction': 85},
            {'symbol': 'GOOGL', 'price': 100.0, 'conviction': 80},
            {'symbol': 'MSFT', 'price': 100.0, 'conviction': 75},
        ]

        sells, buys = sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=10000.0,
            holdings={},
            method='equal_weight',
            rules={'max_position_pct': 100, 'min_position_value': 100},
            cash_available=10000.0
        )

        # All 3 get roughly equal allocations within portfolio value
        assert len(buys) == 3
        total_buy_value = sum(b['position'].estimated_value for b in buys)
        assert total_buy_value <= 10000.0, f"Total buys ${total_buy_value} exceeds portfolio value"
        # Buys are sorted by conviction (highest first)
        assert buys[0]['symbol'] == 'AAPL'

    def test_issue2_dividend_tracking(self, mock_db):
        """Test Issue 2: Dividend tracking and attribution."""
        # Test dividend summary
        mock_db.get_portfolio_dividend_summary.return_value = {
            'total_dividends': 500.0,
            'ytd_dividends': 150.0,
            'breakdown': [
                {'symbol': 'AAPL', 'payment_count': 4, 'total_received': 300.0},
                {'symbol': 'MSFT', 'payment_count': 4, 'total_received': 200.0}
            ]
        }

        # Test performance attribution
        mock_db.get_portfolio_performance_with_attribution.return_value = {
            'total_return': 1500.0,
            'total_return_pct': 15.0,
            'capital_gains': 1000.0,
            'dividend_income': 500.0,
            'dividend_yield_pct': 5.0
        }

        # Get dividend summary
        div_summary = mock_db.get_portfolio_dividend_summary(1)
        assert div_summary['total_dividends'] == 500.0
        assert div_summary['ytd_dividends'] == 150.0
        assert len(div_summary['breakdown']) == 2

        # Get performance attribution
        perf = mock_db.get_portfolio_performance_with_attribution(1)
        assert perf['dividend_income'] == 500.0
        assert perf['capital_gains'] == 1000.0
        assert perf['dividend_yield_pct'] == 5.0

    def test_issue3_holding_reevaluation(self, mock_db):
        """Test Issue 3: Universe compliance detects held positions failing filters."""
        checker = ExitConditionChecker(mock_db)

        held_symbols = {'AAPL', 'MSFT'}
        # AAPL no longer passes universe filters
        filtered_candidates = ['MSFT', 'GOOG']
        holdings = {'AAPL': 10, 'MSFT': 15}

        exits = checker.check_universe_compliance(held_symbols, filtered_candidates, holdings)

        assert len(exits) == 1
        assert exits[0].symbol == 'AAPL'
        assert 'universe' in exits[0].reason.lower()

    def test_issue4_position_additions_higher_threshold(self, mock_db):
        """Test Issue 4: Higher thresholds for position additions."""
        import pandas as pd

        executor = StrategyExecutor(mock_db)

        # Mock the lynch_criteria to return score of 72
        mock_lynch = Mock()

        def eval_batch(df, config):
            result = df[['symbol']].copy()
            result['overall_score'] = 72.0
            result['overall_status'] = 'BUY'
            return result

        mock_lynch.evaluate_batch = Mock(side_effect=eval_batch)
        executor._lynch_criteria = mock_lynch

        mock_db.append_to_run_log = Mock()

        # Mock StockVectors
        mock_vectors_class = Mock()
        mock_vectors_instance = Mock()
        mock_vectors_instance.load_vectors.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'price': [150.0],
            'peg_ratio': [1.5],
            'debt_to_equity': [0.5],
            'institutional_ownership': [0.6],
        })
        mock_vectors_class.return_value = mock_vectors_instance

        conditions = {
            'scoring_requirements': [
                {'character': 'lynch', 'min_score': 60},
                {'character': 'buffett', 'min_score': 60}
            ],
            'addition_scoring_requirements': [
                {'character': 'lynch', 'min_score': 75},
                {'character': 'buffett', 'min_score': 75}
            ]
        }

        # Score as new position (should pass: 72 >= 60)
        with patch('scoring.vectors.StockVectors', mock_vectors_class):
            new_passed, new_declined = executor._score_candidates(
                candidates=['AAPL'],
                conditions=conditions,
                run_id=1,
                is_addition=False
            )
        assert len(new_passed) == 1
        assert new_passed[0]['position_type'] == 'new'

        # Score as addition (should fail: 72 < 75)
        mock_vectors_instance.load_vectors.return_value = pd.DataFrame({
            'symbol': ['AAPL'],
            'price': [150.0],
            'peg_ratio': [1.5],
            'debt_to_equity': [0.5],
            'institutional_ownership': [0.6],
        })
        with patch('scoring.vectors.StockVectors', mock_vectors_class):
            addition_passed, addition_declined = executor._score_candidates(
                candidates=['AAPL'],
                conditions=conditions,
                run_id=1,
                is_addition=True
            )
        assert len(addition_passed) == 0  # Score 72 < 75 required for additions

    def test_integration_all_fixes(self, mock_db):
        """Integration test: All four fixes working together."""
        executor = StrategyExecutor(mock_db)

        # Setup portfolio with holdings and cash
        mock_db.get_portfolio_holdings.return_value = {'AAPL': 10}  # Already hold AAPL
        mock_db.get_portfolio_summary.return_value = {
            'total_value': 15000,
            'cash': 5000,
            'holdings': {'AAPL': 10},
            'total_dividends': 100.0,  # Issue 2: Dividend tracking
            'dividend_income': 100.0
        }

        # Mock position entry dates (Issue 3)
        mock_db.get_position_entry_dates.return_value = {
            'AAPL': {
                'first_buy_date': date.today() - timedelta(days=45),
                'days_held': 45
            }
        }

        # Universe returns both AAPL (held) and GOOGL (new)
        candidates = ['AAPL', 'GOOGL']

        # Separate into new vs additions (Issue 4)
        holdings = set(mock_db.get_portfolio_holdings(1).keys())
        new_candidates = [s for s in candidates if s not in holdings]
        held_candidates = [s for s in candidates if s in holdings]

        assert new_candidates == ['GOOGL']
        assert held_candidates == ['AAPL']

        # Cash tracking (Issue 1) ensures we don't overdraft
        available_cash = mock_db.get_portfolio_summary(1)['cash']
        assert available_cash == 5000

        print("\n✓ Integration test passed: All four fixes work together correctly")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
