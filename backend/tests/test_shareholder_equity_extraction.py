# ABOUTME: Tests for shareholder_equity extraction from yfinance balance sheet data
# ABOUTME: Verifies the helper and that earnings pipeline stores equity for annual and quarterly paths

import sys
import os
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

from data_fetcher.financials import FinancialsMixin
from data_fetcher.earnings import EarningsMixin


# ── Minimal concrete classes (no DB needed for pure extraction tests) ────────

class MinimalFetcher(FinancialsMixin):
    pass


class MinimalDataFetcher(EarningsMixin, FinancialsMixin):
    """Combines both mixins to test methods that span both."""
    pass


fetcher = MinimalFetcher()


def _make_balance_sheet(equity_key: str, equity_value, col=None):
    """Build a minimal fake balance sheet DataFrame."""
    if col is None:
        col = pd.Timestamp('2023-12-31')
    return pd.DataFrame(
        {col: {equity_key: equity_value, 'Total Debt': 1_000_000.0}},
    )


# ══════════════════════════════════════════════════════════════════════════════
# _extract_shareholder_equity helper
# ══════════════════════════════════════════════════════════════════════════════

class TestExtractShareholderEquity:

    def test_stockholders_equity_key(self):
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Stockholders Equity', 5_000_000.0, col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result == 5_000_000.0

    def test_common_stock_equity_key(self):
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Common Stock Equity', 3_500_000.0, col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result == 3_500_000.0

    def test_total_equity_gross_minority_interest_key(self):
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Total Equity Gross Minority Interest', 7_200_000.0, col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result == 7_200_000.0

    def test_total_stockholder_equity_key(self):
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Total Stockholder Equity', 4_100_000.0, col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result == 4_100_000.0

    def test_returns_none_when_key_missing(self):
        col = pd.Timestamp('2023-12-31')
        bs = pd.DataFrame({col: {'Total Debt': 1_000_000.0}})
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result is None

    def test_returns_none_for_nan_value(self):
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Stockholders Equity', float('nan'), col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result is None

    def test_returns_none_for_empty_balance_sheet(self):
        col = pd.Timestamp('2023-12-31')
        bs = pd.DataFrame()
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result is None

    def test_returns_negative_equity(self):
        """Negative equity is valid data and should be returned as-is."""
        col = pd.Timestamp('2023-12-31')
        bs = _make_balance_sheet('Stockholders Equity', -500_000.0, col)
        result = fetcher._extract_shareholder_equity(bs, col)
        assert result == -500_000.0


# ══════════════════════════════════════════════════════════════════════════════
# _fetch_and_store_earnings - annual section stores shareholder_equity
# ══════════════════════════════════════════════════════════════════════════════

class TestFetchAndStoreEarningsPassesEquity:
    """Verify that shareholder_equity is extracted and passed to save_earnings_history."""

    def _make_financials(self, col):
        return pd.DataFrame({col: {
            'Total Revenue': 100_000_000.0,
            'Diluted EPS': 2.5,
            'Net Income': 10_000_000.0,
        }})

    def _make_balance_sheet(self, col):
        return pd.DataFrame({col: {
            'Stockholders Equity': 50_000_000.0,
            'Total Debt': 20_000_000.0,
        }})

    def _make_cashflow(self, col):
        return pd.DataFrame({col: {
            'Operating Cash Flow': 15_000_000.0,
            'Capital Expenditure': -2_000_000.0,
        }})

    def _build_fetcher_with_mocks(self, financials, balance_sheet, cashflow):
        mock_db = MagicMock()
        f = MinimalDataFetcher.__new__(MinimalDataFetcher)
        f.db = mock_db
        # Patch all yfinance fetch methods
        f._get_yf_financials = MagicMock(return_value=financials)
        f._get_yf_balance_sheet = MagicMock(return_value=balance_sheet)
        f._get_yf_cashflow = MagicMock(return_value=cashflow)
        f._get_yf_dividends = MagicMock(return_value=pd.Series([], dtype=float))
        f._get_yf_history = MagicMock(return_value=None)
        f._get_yf_quarterly_financials = MagicMock(return_value=pd.DataFrame())
        f._get_yf_quarterly_balance_sheet = MagicMock(return_value=pd.DataFrame())
        return f

    def test_annual_save_includes_shareholder_equity(self):
        col = pd.Timestamp('2023-12-31')
        f = self._build_fetcher_with_mocks(
            self._make_financials(col),
            self._make_balance_sheet(col),
            self._make_cashflow(col),
        )

        f._fetch_and_store_earnings('TEST')

        # save_earnings_history must have been called with shareholder_equity=50_000_000.0
        assert f.db.save_earnings_history.called
        kwargs = f.db.save_earnings_history.call_args_list[0][1]
        assert kwargs.get('shareholder_equity') == 50_000_000.0

    def test_annual_save_passes_none_when_no_balance_sheet(self):
        col = pd.Timestamp('2023-12-31')
        f = self._build_fetcher_with_mocks(
            self._make_financials(col),
            pd.DataFrame(),   # empty balance sheet
            self._make_cashflow(col),
        )

        f._fetch_and_store_earnings('TEST')

        assert f.db.save_earnings_history.called
        kwargs = f.db.save_earnings_history.call_args_list[0][1]
        assert kwargs.get('shareholder_equity') is None


# ══════════════════════════════════════════════════════════════════════════════
# _fetch_quarterly_earnings stores shareholder_equity
# ══════════════════════════════════════════════════════════════════════════════

class TestFetchQuarterlyEarningsPassesEquity:

    def _make_quarterly_financials(self, col):
        return pd.DataFrame({col: {
            'Total Revenue': 25_000_000.0,
            'Diluted EPS': 0.65,
            'Net Income': 2_600_000.0,
        }})

    def _make_quarterly_balance_sheet(self, col):
        return pd.DataFrame({col: {
            'Stockholders Equity': 48_000_000.0,
            'Total Debt': 18_000_000.0,
        }})

    def _build_fetcher_with_mocks(self, q_financials, q_balance_sheet):
        mock_db = MagicMock()
        f = MinimalDataFetcher.__new__(MinimalDataFetcher)
        f.db = mock_db
        f._get_yf_quarterly_financials = MagicMock(return_value=q_financials)
        f._get_yf_quarterly_balance_sheet = MagicMock(return_value=q_balance_sheet)
        f._get_yf_dividends = MagicMock(return_value=pd.Series([], dtype=float))
        f._get_yf_history = MagicMock(return_value=None)
        return f

    def test_quarterly_save_includes_shareholder_equity(self):
        col = pd.Timestamp('2023-09-30')
        f = self._build_fetcher_with_mocks(
            self._make_quarterly_financials(col),
            self._make_quarterly_balance_sheet(col),
        )

        f._fetch_quarterly_earnings('TEST')

        assert f.db.save_earnings_history.called
        kwargs = f.db.save_earnings_history.call_args_list[0][1]
        assert kwargs.get('shareholder_equity') == 48_000_000.0

    def test_quarterly_save_passes_none_when_no_balance_sheet(self):
        col = pd.Timestamp('2023-09-30')
        f = self._build_fetcher_with_mocks(
            self._make_quarterly_financials(col),
            pd.DataFrame(),   # empty
        )

        f._fetch_quarterly_earnings('TEST')

        assert f.db.save_earnings_history.called
        kwargs = f.db.save_earnings_history.call_args_list[0][1]
        assert kwargs.get('shareholder_equity') is None
