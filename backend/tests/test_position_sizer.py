# ABOUTME: Tests for target-portfolio position sizing logic
# ABOUTME: Validates calculate_target_orders produces correct buy/sell signals

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategy_executor.position_sizing import PositionSizer
from strategy_executor.models import PositionSize, ExitSignal


class TestPositionSizer(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.sizer = PositionSizer(self.mock_db)

    def test_min_position_value_respected(self):
        """Drift below min_position_value produces no buy signal."""
        # Target $500 (5% of $10k) but min is $1000 → no buy
        candidates = [{'symbol': 'AAPL', 'price': 150.0, 'conviction': 50}]
        rules = {
            'fixed_position_pct': 5,
            'max_position_pct': 20,
            'min_position_value': 1000
        }

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=10000.0,
            holdings={},
            method='fixed_pct',
            rules=rules,
            cash_available=5000.0
        )

        self.assertEqual(len(buys), 0, "Should skip trade as $500 < $1000 min_position_value")

    def test_min_position_value_allows_large_trade(self):
        """Drift above min_position_value produces a buy signal."""
        # Target $1500 (15% of $10k) with min $1000 → buy
        candidates = [{'symbol': 'AAPL', 'price': 150.0, 'conviction': 50}]
        rules = {
            'fixed_position_pct': 15,
            'max_position_pct': 20,
            'min_position_value': 1000
        }

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=10000.0,
            holdings={},
            method='fixed_pct',
            rules=rules,
            cash_available=5000.0
        )

        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0]['position'].shares, 10)  # $1500 / $150 = 10
        self.assertEqual(buys[0]['position'].estimated_value, 1500.0)

    def test_basic_buy(self):
        """Single candidate with no existing holdings produces a buy signal."""
        candidates = [{'symbol': 'AAPL', 'price': 150.0, 'conviction': 50}]
        rules = {
            'fixed_position_pct': 10,
            'max_position_pct': 20,
            'min_position_value': 100
        }

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=10000.0,
            holdings={},
            method='fixed_pct',
            rules=rules,
            cash_available=5000.0
        )

        # Target $1000 / $150 = 6 shares
        self.assertEqual(len(buys), 1)
        self.assertEqual(buys[0]['symbol'], 'AAPL')
        self.assertEqual(buys[0]['position'].shares, 6)
        self.assertAlmostEqual(buys[0]['position'].estimated_value, 900.0)


class TestBuyPrioritization(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.sizer = PositionSizer(self.mock_db)

    def test_buys_sorted_by_conviction(self):
        """Higher-conviction candidate appears first in buy signals."""
        candidates = [
            {'symbol': 'LOW_CONV', 'price': 100.0, 'conviction': 40},
            {'symbol': 'HIGH_CONV', 'price': 100.0, 'conviction': 80},
        ]
        rules = {'max_position_pct': 20, 'min_position_value': 100}

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=50000.0,
            holdings={},
            method='equal_weight',
            rules=rules,
            cash_available=10000.0
        )

        self.assertGreaterEqual(len(buys), 2)
        self.assertEqual(buys[0]['symbol'], 'HIGH_CONV')
        self.assertEqual(buys[1]['symbol'], 'LOW_CONV')


class TestRebalancingTrims(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.sizer = PositionSizer(self.mock_db)

    def test_over_weight_generates_trim(self):
        """Over-weight holding generates a trim signal to bring it to equal-weight target."""
        # Universe: AAPL (held) + MSFT (new) → N=2, target=$1000 each in $2000 portfolio
        # AAPL: 20 shares @ $100 = $2000, which is 2× the $1000 target
        candidates = [
            {'symbol': 'AAPL', 'price': 100.0, 'conviction': 70},
            {'symbol': 'MSFT', 'price': 100.0, 'conviction': 70},
        ]
        rules = {'max_position_pct': 100, 'min_position_value': 100}

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=2000.0,
            holdings={'AAPL': 20},
            method='equal_weight',
            rules=rules,
            cash_available=0.0
        )

        # AAPL should be trimmed from 20 to 10 shares
        trim_signals = [s for s in sells if s.exit_type == 'trim']
        self.assertEqual(len(trim_signals), 1)
        self.assertEqual(trim_signals[0].symbol, 'AAPL')
        self.assertEqual(trim_signals[0].quantity, 10)

    def test_at_weight_no_trim(self):
        """Holding exactly at target weight produces no trim."""
        # Universe: AAPL + MSFT → target=$1000. AAPL is at $1000 (10 shares @ $100).
        candidates = [
            {'symbol': 'AAPL', 'price': 100.0, 'conviction': 70},
            {'symbol': 'MSFT', 'price': 100.0, 'conviction': 70},
        ]
        rules = {'max_position_pct': 100, 'min_position_value': 100}

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=2000.0,
            holdings={'AAPL': 10},
            method='equal_weight',
            rules=rules,
            cash_available=1000.0
        )

        trim_signals = [s for s in sells if s.exit_type == 'trim']
        self.assertEqual(len(trim_signals), 0)

    def test_empty_candidates_no_holdings_returns_empty(self):
        """No candidates and no holdings → no signals."""
        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=[],
            portfolio_value=10000.0,
            holdings={},
            method='equal_weight',
            rules={'max_position_pct': 100, 'min_position_value': 100},
            cash_available=5000.0
        )

        self.assertEqual(sells, [])
        self.assertEqual(buys, [])

    def test_conviction_weighted_trim(self):
        """Over-weight holding trimmed to its conviction-proportional target."""
        # AAPL conviction=80, TSLA conviction=20 → targets 80%/20% of $10k
        # AAPL target=$8000: 45 shares @ $200 = $9000 → trim 5 shares ($1000 excess)
        candidates = [
            {'symbol': 'AAPL', 'price': 200.0, 'conviction': 80},
            {'symbol': 'TSLA', 'price': 100.0, 'conviction': 20},
        ]
        rules = {'max_position_pct': 100, 'min_position_value': 100}

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=10000.0,
            holdings={'AAPL': 45, 'TSLA': 10},
            method='conviction_weighted',
            rules=rules,
            cash_available=0.0
        )

        trim_symbols = [s.symbol for s in sells if s.exit_type == 'trim']
        self.assertIn('AAPL', trim_symbols)
        self.assertNotIn('TSLA', trim_symbols)
        aapl_trim = next(s for s in sells if s.symbol == 'AAPL')
        self.assertEqual(aapl_trim.quantity, 5)

    def test_trim_does_not_full_exit(self):
        """Trim quantity is always less than total shares held (partial sell only)."""
        # AAPL: 30 shares @ $100 = $3000. In 4-stock equal-weight portfolio of $4000,
        # target = $1000. Should sell 20 shares, keep 10.
        candidates = [
            {'symbol': 'AAPL', 'price': 100.0, 'conviction': 70},
            {'symbol': 'MSFT', 'price': 100.0, 'conviction': 70},
            {'symbol': 'GOOG', 'price': 100.0, 'conviction': 70},
            {'symbol': 'TSLA', 'price': 100.0, 'conviction': 70},
        ]
        rules = {'max_position_pct': 100, 'min_position_value': 100}

        sells, buys = self.sizer.calculate_target_orders(
            section_id=1,
            candidates=candidates,
            portfolio_value=4000.0,
            holdings={'AAPL': 30},
            method='equal_weight',
            rules=rules,
            cash_available=1000.0
        )

        trim_signals = [s for s in sells if s.exit_type == 'trim']
        self.assertEqual(len(trim_signals), 1)
        trim = trim_signals[0]
        self.assertEqual(trim.quantity, 20)
        self.assertLess(trim.quantity, 30, "Trim must not sell entire position")
        self.assertEqual(trim.exit_type, 'trim')


if __name__ == '__main__':
    unittest.main()
