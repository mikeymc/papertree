# ABOUTME: Tests for automated trading alert execution in the background worker
# ABOUTME: Validates that triggered alerts execute trades and respect market hours

import sys
import os
import json
import logging
import unittest
from unittest.mock import MagicMock, patch


# sys.path handled by conftest.py

from worker import BackgroundWorker

class TestTradingAlerts(unittest.TestCase):
    def setUp(self):
        with patch('database.Database'):
            self.worker = BackgroundWorker()

        # Mock database interactions
        self.worker.db = MagicMock()

        # Mock portfolio service (it's imported in worker.alert_jobs, so we patch it there)
        self.patcher = patch('worker.alert_jobs.portfolio_service')
        self.mock_portfolio_service = self.patcher.start()

        # Mock the genai module that alert_jobs imports via `from google import genai`
        self.mock_genai_module = MagicMock()
        self.mock_genai_instance = MagicMock()
        self.mock_genai_module.Client.return_value = self.mock_genai_instance

        # Save and replace google.genai in sys.modules so `from google import genai` finds our mock
        import google
        self._saved_genai = getattr(google, 'genai', None)
        google.genai = self.mock_genai_module

        # Set GEMINI_API_KEY so the code doesn't bail early
        self.patcher_env = patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'})
        self.patcher_env.start()

    def tearDown(self):
        self.patcher.stop()
        self.patcher_env.stop()
        # Restore google.genai
        import google
        if self._saved_genai is not None:
            google.genai = self._saved_genai
        else:
            delattr(google, 'genai')

    def test_automated_trade_execution(self):
        """Test that a triggered alert with action_type executes a trade."""

        # Setup mock alert data
        alert_id = 999
        symbol = "TEST"
        portfolio_id = 123
        quantity = 10

        mock_alert = {
            'id': alert_id,
            'symbol': symbol,
            'condition_type': 'custom',
            'condition_params': {},
            'condition_description': 'Price drops',
            'action_type': 'market_buy',
            'action_payload': {'quantity': quantity},
            'portfolio_id': portfolio_id,
            'action_note': 'Test Buy',
            'status': 'active'
        }

        # Mock db responses
        self.worker.db.get_all_active_alerts.return_value = [mock_alert]
        self.worker.db.get_stock_metrics.return_value = {'price': 100.0, 'pe_ratio': 10.0}
        self.worker.db.get_insider_trades.return_value = []
        self.worker.db.get_material_events.return_value = []
        self.worker.db.get_earnings_history.return_value = []
        self.worker.db.get_weekly_prices.return_value = {}

        # Mock LLM to force trigger
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "triggered": True,
            "reason": "Test condition met"
        })
        self.mock_genai_instance.models.generate_content.return_value = mock_response

        # Mock trade execution success
        self.mock_portfolio_service.execute_trade.return_value = {
            'success': True,
            'transaction_id': 1,
            'price_per_share': 100.0,
            'total_value': 1000.0
        }

        # Run check_alerts
        self.worker._run_check_alerts(job_id=1, params={})

        # Verify execute_trade was called correctly
        self.mock_portfolio_service.execute_trade.assert_called_once()
        call_args = self.mock_portfolio_service.execute_trade.call_args[1]

        self.assertEqual(call_args['portfolio_id'], portfolio_id)
        self.assertEqual(call_args['symbol'], symbol)
        self.assertEqual(call_args['transaction_type'], 'BUY') # market_buy -> BUY
        self.assertEqual(call_args['quantity'], quantity)
        self.assertIn("Test Buy", call_args['note'])

        # Verify alert status update contains trade result
        self.worker.db.update_alert_status.assert_called_once()
        status_args = self.worker.db.update_alert_status.call_args[1]

        message = status_args.get('message')
        self.assertIn("Auto-Trade: Executed BUY 10 shares", message)

    def test_automated_trade_skipped_if_not_triggered(self):
        """Test that trade is NOT executed if alert is active but not triggered."""

        mock_alert = {
            'id': 888,
            'symbol': 'TEST',
            'action_type': 'market_buy',
            'portfolio_id': 1,
            'action_payload': {'quantity': 5},
            'condition_type': 'custom',
            'condition_params': {},
            'status': 'active'
        }

        self.worker.db.get_all_active_alerts.return_value = [mock_alert]
        self.worker.db.get_stock_metrics.return_value = {'price': 50}
        self.worker.db.get_insider_trades.return_value = []
        self.worker.db.get_material_events.return_value = []
        self.worker.db.get_earnings_history.return_value = []
        self.worker.db.get_weekly_prices.return_value = {}

        # Mock LLM to NOT trigger
        mock_response = MagicMock()
        mock_response.text = json.dumps({"triggered": False, "reason": "No change"})
        self.mock_genai_instance.models.generate_content.return_value = mock_response

        self.worker._run_check_alerts(job_id=2, params={})

        self.mock_portfolio_service.execute_trade.assert_not_called()

    def test_hold_off_when_market_closed(self):
        """Test that trading alerts are skipped (held off) when market is closed."""

        mock_alert = {
            'id': 777,
            'symbol': 'TEST',
            'action_type': 'market_buy',
            'portfolio_id': 1,
            'action_payload': {'quantity': 5},
            'condition_type': 'custom',
            'condition_params': {},
            'status': 'active'
        }

        self.worker.db.get_all_active_alerts.return_value = [mock_alert]

        # Mock market closed
        self.mock_portfolio_service.is_market_open.return_value = False

        self.worker._run_check_alerts(job_id=3, params={})

        # Verify we didn't even fetch metrics or call LLM (because we skipped early)
        self.worker.db.get_stock_metrics.assert_not_called()
        self.mock_genai_instance.models.generate_content.assert_not_called()
        self.mock_portfolio_service.execute_trade.assert_not_called()

if __name__ == '__main__':
    unittest.main()
