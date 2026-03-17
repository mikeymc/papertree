# ABOUTME: Tests for benchmark tracker alpha calculation
# ABOUTME: Verifies SPY return uses latest benchmark, not exact date match

import pytest
from unittest.mock import MagicMock
from datetime import date

from market_data.benchmark import BenchmarkTracker


class TestRecordStrategyPerformance:
    """Verify alpha calculation uses latest benchmark snapshot."""

    def setup_method(self):
        self.db = MagicMock()
        self.tracker = BenchmarkTracker(self.db)

    def test_uses_latest_benchmark_when_no_snapshot_for_today(self):
        """When no benchmark exists for today, should use latest available."""
        self.db.get_strategy_inception_data.return_value = {
            'portfolio_value': 100000,
            'spy_price': 480.0,
        }
        # No snapshot for today's exact date
        self.db.get_benchmark_snapshot.return_value = None
        # But latest snapshot exists
        self.db.get_latest_benchmark_snapshot.return_value = {'spy_price': 500.0}

        result = self.tracker.record_strategy_performance(1, 110000)

        # portfolio_return = (110000 - 100000) / 100000 * 100 = 10%
        # spy_return = (500 - 480) / 480 * 100 = 4.1667%
        # alpha = 10 - 4.1667 = 5.8333
        assert result['portfolio_return_pct'] == pytest.approx(10.0)
        assert result['spy_return_pct'] == pytest.approx(4.1667, rel=1e-3)
        assert result['alpha'] == pytest.approx(5.8333, rel=1e-3)

    def test_spy_return_not_zero_when_spy_changed(self):
        """Alpha should not equal portfolio return when SPY has moved."""
        self.db.get_strategy_inception_data.return_value = {
            'portfolio_value': 100000,
            'spy_price': 480.0,
        }
        self.db.get_benchmark_snapshot.return_value = None
        self.db.get_latest_benchmark_snapshot.return_value = {'spy_price': 500.0}

        result = self.tracker.record_strategy_performance(1, 110000)

        assert result['spy_return_pct'] != 0
        assert result['alpha'] != result['portfolio_return_pct']

    def test_prefers_todays_snapshot_when_available(self):
        """When today's snapshot exists, use it (no regression)."""
        self.db.get_strategy_inception_data.return_value = {
            'portfolio_value': 100000,
            'spy_price': 480.0,
        }
        self.db.get_benchmark_snapshot.return_value = {'spy_price': 510.0}

        result = self.tracker.record_strategy_performance(1, 110000)

        # Should use today's snapshot (510), not call get_latest
        spy_return = ((510.0 - 480.0) / 480.0) * 100
        assert result['spy_return_pct'] == pytest.approx(spy_return)
        self.db.get_latest_benchmark_snapshot.assert_not_called()

    def test_first_run_uses_latest_benchmark_for_inception(self):
        """On first run with no inception data, uses latest benchmark."""
        self.db.get_strategy_inception_data.return_value = None
        self.db.get_benchmark_snapshot.return_value = None
        self.db.get_latest_benchmark_snapshot.return_value = {'spy_price': 500.0}

        result = self.tracker.record_strategy_performance(1, 100000)

        # First run: inception == current, so returns should be 0
        assert result['portfolio_return_pct'] == 0
        assert result['spy_return_pct'] == 0
        assert result['alpha'] == 0
