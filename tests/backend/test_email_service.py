# ABOUTME: Tests for the email briefing service
# ABOUTME: Validates briefing email template rendering and send logic via Resend

import pytest
from unittest.mock import patch, MagicMock
import json


class TestSendBriefingEmail:
    """Tests for send_briefing_email function."""

    @pytest.fixture
    def sample_briefing(self):
        return {
            'portfolio_value': 105000.0,
            'portfolio_return_pct': 5.0,
            'spy_return_pct': 3.0,
            'alpha': 2.0,
            'executive_summary': 'Portfolio performed well this week.',
            'buys_json': json.dumps([
                {'symbol': 'AAPL', 'shares': 10, 'price': 150.0}
            ]),
            'sells_json': json.dumps([]),
            'trades_executed': 1,
            'stocks_screened': 500,
        }

    @patch('email_service.resend.Emails.send')
    def test_sends_email_with_correct_recipient(self, mock_send, sample_briefing):
        from email_service import send_briefing_email
        mock_send.return_value = {'id': 'test-id'}

        with patch.dict('os.environ', {'RESEND_API_KEY': 'test-key'}):
            result = send_briefing_email('user@example.com', sample_briefing, 'My Portfolio')

        assert result is True
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        assert call_args['to'] == 'user@example.com'

    @patch('email_service.resend.Emails.send')
    def test_email_subject_contains_portfolio_name(self, mock_send, sample_briefing):
        from email_service import send_briefing_email
        mock_send.return_value = {'id': 'test-id'}

        with patch.dict('os.environ', {'RESEND_API_KEY': 'test-key'}):
            send_briefing_email('user@example.com', sample_briefing, 'GARP Strategy')

        call_args = mock_send.call_args[0][0]
        assert 'GARP Strategy' in call_args['subject']

    @patch('email_service.resend.Emails.send')
    def test_email_body_contains_key_metrics(self, mock_send, sample_briefing):
        from email_service import send_briefing_email
        mock_send.return_value = {'id': 'test-id'}

        with patch.dict('os.environ', {'RESEND_API_KEY': 'test-key'}):
            send_briefing_email('user@example.com', sample_briefing, 'Test')

        call_args = mock_send.call_args[0][0]
        html = call_args['html']
        assert '$105,000' in html
        assert '5.00%' in html
        assert 'AAPL' in html

    def test_returns_false_when_resend_not_configured(self, sample_briefing):
        from email_service import send_briefing_email

        with patch.dict('os.environ', {}, clear=True):
            result = send_briefing_email('user@example.com', sample_briefing, 'Test')

        assert result is False

    @patch('email_service.resend.Emails.send')
    def test_returns_false_on_send_error(self, mock_send, sample_briefing):
        from email_service import send_briefing_email
        mock_send.side_effect = Exception("API error")

        with patch.dict('os.environ', {'RESEND_API_KEY': 'test-key'}):
            result = send_briefing_email('user@example.com', sample_briefing, 'Test')

        assert result is False


class TestBuildBriefingHtml:
    """Tests for HTML template rendering."""

    def test_renders_executive_summary(self):
        from email_service import build_briefing_html
        briefing = {
            'executive_summary': 'Great week for the portfolio.',
            'portfolio_value': 100000,
            'portfolio_return_pct': 2.5,
            'spy_return_pct': 1.0,
            'alpha': 1.5,
            'buys_json': '[]',
            'sells_json': '[]',
            'trades_executed': 0,
        }
        html = build_briefing_html(briefing, 'My Portfolio')
        assert 'Great week for the portfolio.' in html

    def test_renders_buy_trades(self):
        from email_service import build_briefing_html
        briefing = {
            'executive_summary': 'Added a position.',
            'portfolio_value': 100000,
            'portfolio_return_pct': 0,
            'spy_return_pct': 0,
            'alpha': 0,
            'buys_json': json.dumps([
                {'symbol': 'MSFT', 'shares': 5, 'price': 400.0}
            ]),
            'sells_json': '[]',
            'trades_executed': 1,
        }
        html = build_briefing_html(briefing, 'Test')
        assert 'MSFT' in html
        assert 'BUY' in html

    def test_renders_sell_trades(self):
        from email_service import build_briefing_html
        briefing = {
            'executive_summary': 'Exited a position.',
            'portfolio_value': 100000,
            'portfolio_return_pct': 0,
            'spy_return_pct': 0,
            'alpha': 0,
            'buys_json': '[]',
            'sells_json': json.dumps([
                {'symbol': 'TSLA', 'shares': 3, 'price': 250.0}
            ]),
            'trades_executed': 1,
        }
        html = build_briefing_html(briefing, 'Test')
        assert 'TSLA' in html
        assert 'SELL' in html
