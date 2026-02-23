# ABOUTME: Tests for worker memory optimizations (OOM fixes)
# ABOUTME: Validates cache clearing and counter accuracy during stock screening

import pytest
from unittest.mock import Mock, MagicMock, patch
from worker import BackgroundWorker
import gc

class TestWorkerMemoryOptimization:
    """Tests for worker memory optimizations (OOM fixes)"""

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.claim_pending_job = Mock(return_value=None)
        db.update_job_progress = Mock()
        db.update_session_progress = Mock()
        db.complete_job = Mock()
        db.complete_session = Mock()
        db.get_background_job = Mock(return_value={'status': 'running'})
        db.get_pool_stats = Mock(return_value={
            'current_in_use': 1, 'pool_size': 10, 'peak_in_use': 2
        })
        return db

    @patch('market_data.tradingview.TradingViewFetcher')
    @patch('finviz_fetcher.FinvizFetcher')
    @patch('data_fetcher.DataFetcher')
    def test_run_screening_clears_cache_and_counts_correctly(
        self,
        MockDataFetcher, MockFinvizFetcher, MockTVFetcher,
        mock_db
    ):
        """
        Verify that:
        1. Market data and Finviz cache entries are deleted after processing
        2. Counters (total_analyzed/total_symbols/failed_count) are calculated correctly
        """
        # Setup mocks
        worker = BackgroundWorker()
        worker.db = mock_db

        # Test data - 20 stocks
        stocks = {f'SYM{i}': {'price': 100} for i in range(20)}

        market_data_cache_ref = stocks.copy()
        MockTVFetcher.return_value.fetch_all_stocks.return_value = market_data_cache_ref

        finviz_cache_ref = {f'SYM{i}': 0.5 for i in range(20)}
        MockFinvizFetcher.return_value.fetch_all_institutional_ownership.return_value = finviz_cache_ref

        # Mock DataFetcher to return something
        MockDataFetcher.return_value.fetch_stock_data.return_value = {'some': 'data'}

        # Run screening
        job = {
            'id': 123,
            'job_type': 'full_screening',
            'params': {
                'limit': 20,
                'session_id': 999,
                'algorithm': 'weighted'
            }
        }

        worker._execute_job(job)

        # Verify cache entries are deleted after processing
        assert len(market_data_cache_ref) == 0, "Market data cache should be empty after processing"
        assert len(finviz_cache_ref) == 0, "Finviz cache should be empty after processing"

        # Verify counters
        mock_db.complete_job.assert_called_once()
        result_arg = mock_db.complete_job.call_args[0][1]

        assert result_arg['total_analyzed'] == 20
        assert result_arg['total_symbols'] == 20
        assert result_arg['failed_count'] == 0
