# ABOUTME: Tests for dashboard and market data endpoints
# ABOUTME: Verifies /api/market/index, /api/market/movers, and /api/dashboard work correctly

import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import date


@pytest.fixture
def mock_db():
    """Create a mock database."""
    db = MagicMock()
    db.get_connection.return_value = MagicMock()
    db.return_connection = MagicMock()
    db.get_watchlist.return_value = ['AAPL', 'GOOGL']
    db.get_user_portfolios.return_value = []
    db.get_alerts.return_value = []
    db.get_user_strategies.return_value = []
    db.get_portfolio_holdings.return_value = {}
    return db


@pytest.fixture
def app(mock_db):
    """Create test Flask app."""
    with patch.dict('sys.modules', {
        'google.genai': MagicMock(),
        'google.genai.types': MagicMock(),
    }):
        with patch.dict(os.environ, {
            'FINNHUB_API_KEY': 'test_key',
            'SESSION_SECRET_KEY': 'test_secret'
        }):
            with patch('database.Database', return_value=mock_db):
                from app import app as flask_app
                import app.deps as deps
                deps.db = mock_db
                flask_app.config['TESTING'] = True
                yield flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestMarketIndexEndpoint:
    """Tests for GET /api/market/index/<symbol>"""

    def test_unsupported_index_returns_400(self, client):
        """Test that unsupported index symbols return 400."""
        response = client.get('/api/market/index/INVALID?period=1mo')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_invalid_period_returns_400(self, client):
        """Test that invalid periods return 400."""
        response = client.get('/api/market/index/^GSPC?period=invalid')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


@pytest.fixture
def mock_movers_deps():
    """Helper to mock movers dependencies."""
    import pandas as pd
    mock_scored_df = pd.DataFrame([
        {'symbol': 'AAPL', 'price': 150.0, 'price_change_pct': 2.5, 'overall_status': 'PASS'}
    ])
    
    with patch('app.deps.stock_vectors.load_vectors') as mock_load:
        mock_load.return_value = pd.DataFrame()
        with patch('app.deps.criteria.evaluate_batch') as mock_eval:
            mock_eval.return_value = mock_scored_df
            yield mock_load, mock_eval


class TestMarketMoversEndpoint:
    """Tests for GET /api/market/movers"""

    def test_get_movers_default(self, client, mock_movers_deps):
        """Test getting market movers with defaults."""
        response = client.get('/api/market/movers')
        assert response.status_code == 200
        data = response.get_json()
        assert 'gainers' in data
        assert 'losers' in data
        assert data['period'] == '1d'
        assert len(data['gainers']) > 0
        assert data['gainers'][0]['symbol'] == 'AAPL'

    def test_get_movers_weekly(self, client, mock_db, mock_movers_deps):
        """Test getting market movers with 1w period (historical query)."""
        # Mock the DB historical price query
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'symbol': 'AAPL', 'historical_price': 140.0}
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn
        
        response = client.get('/api/market/movers?period=1w')
        assert response.status_code == 200
        data = response.get_json()
        assert data['period'] == '1w'
        assert len(data['gainers']) > 0
                
    def test_get_movers_weekly_no_error(self, client, mock_db, mock_movers_deps):
        """Verify that 1w period doesn't cause a 500 SQL error."""
        # Minimal mockup to avoid 500 before SQL execution
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn
        
        response = client.get('/api/market/movers?period=1w')
        assert response.status_code == 200


class TestDashboardEndpoint:
    """Tests for GET /api/dashboard"""

    def test_dashboard_requires_auth(self, client):
        """Test that dashboard endpoint requires authentication."""
        import auth
        original_bypass = auth.DEV_AUTH_BYPASS
        auth.DEV_AUTH_BYPASS = False
        try:
            response = client.get('/api/dashboard')
            assert response.status_code == 401
        finally:
            auth.DEV_AUTH_BYPASS = original_bypass


class TestMarketIndexPartialData:
    """Tests for partial data handling in GET /api/market/index"""

    def test_get_market_index_partial_data(self, client):
        """Test that the endpoint handles missing symbols in yfinance download."""
        import pandas as pd
        from unittest.mock import patch

        # MultiIndex columns simulating ^GSPC and ^IXIC returned, but ^DJI missing
        columns = pd.MultiIndex.from_tuples([
            ('^GSPC', 'Close'), ('^GSPC', 'High'), ('^GSPC', 'Low'), ('^GSPC', 'Open'), ('^GSPC', 'Volume'),
            ('^IXIC', 'Close'), ('^IXIC', 'High'), ('^IXIC', 'Low'), ('^IXIC', 'Open'), ('^IXIC', 'Volume')
        ])

        # Mock DataFrame
        mock_df = pd.DataFrame({
            ('^GSPC', 'Close'): [100.0, 105.0],
            ('^GSPC', 'High'): [101.0, 106.0],
            ('^GSPC', 'Low'): [99.0, 104.0],
            ('^GSPC', 'Open'): [99.5, 104.5],
            ('^GSPC', 'Volume'): [1000, 1100],
            ('^IXIC', 'Close'): [200.0, 210.0],
            ('^IXIC', 'High'): [201.0, 211.0],
            ('^IXIC', 'Low'): [199.0, 209.0],
            ('^IXIC', 'Open'): [199.5, 209.5],
            ('^IXIC', 'Volume'): [2000, 2200]
        }, index=pd.to_datetime(['2024-01-01', '2024-01-02']))
        mock_df.columns = columns

        with patch('yfinance.download', return_value=mock_df):
            response = client.get('/api/market/index/^GSPC,^IXIC,^DJI?period=1mo')
            assert response.status_code == 200
            data = response.get_json()

            assert '^GSPC' in data
            assert '^IXIC' in data
            assert '^DJI' in data

            assert 'data' in data['^GSPC']
            assert'current_price' in data['^GSPC']
            assert data['^GSPC']['current_price'] == 105.0

            assert 'data' in data['^IXIC']
            
            assert 'error' in data['^DJI']
            assert 'No data available for ^DJI' in data['^DJI']['error']


class TestDashboardEarningsEndpoint:
    """Tests for GET /api/dashboard/earnings"""

    def test_get_earnings_days_param(self, client, mock_db):
        """Test getting earnings with custom days parameter."""
        mock_cursor = MagicMock()
        # First call is for total count, second for results, others for potential auth/8k status
        mock_cursor.fetchone.side_effect = [{'total': 5}]
        mock_cursor.fetchall.return_value = [
            {'symbol': 'AAPL', 'company_name': 'Apple', 'next_earnings_date': date(2026, 3, 1)}
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn
        mock_db.get_earnings_8k_status_batch.return_value = {}
        mock_db.get_user_by_id.return_value = {"id": 1, "user_type": "regular"}
        
        # Test with days=30
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            
        with patch('app.deps.db', mock_db):
            response = client.get('/api/dashboard/earnings?days=30')
            assert response.status_code == 200
            data = response.get_json()
            assert 'upcoming_earnings' in data
            assert data['upcoming_earnings']['total_count'] == 5
            
            # Verify the SQL matches our expectation (parameterized interval)
            execute_calls = [call for call in mock_cursor.execute.call_args_list]
            found_interval_logic = False
            for call in execute_calls:
                sql = call[0][0]
                params = call[0][1]
                if "%s * INTERVAL '1 day'" in sql:
                    found_interval_logic = True
                    # Check parameter order: days should be first, symbols second
                    assert params[0] == 30
                    assert isinstance(params[1], list)
                    assert "sm.symbol = ANY(%s)" in sql
                    break
            assert found_interval_logic

    def test_get_earnings_scope_all(self, client, mock_db):
        """Test getting earnings with scope=all parameter."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 100}
        mock_cursor.fetchall.return_value = [
            {'symbol': 'MSFT', 'company_name': 'Microsoft', 'next_earnings_date': date(2026, 3, 1)}
        ]
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_connection.return_value = mock_conn
        mock_db.get_earnings_8k_status_batch.return_value = {}
        mock_db.get_user_by_id.return_value = {"id": 1, "user_type": "regular"}
        
        # Test with scope=all
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            
        with patch('app.deps.db', mock_db):
            response = client.get('/api/dashboard/earnings?scope=all')
            assert response.status_code == 200
            data = response.get_json()
            assert data['upcoming_earnings']['total_count'] == 100
            
            # Verify the SQL DOES NOT contain the watchlist filtering
            execute_calls = [call for call in mock_cursor.execute.call_args_list]
            for call in execute_calls:
                sql = call[0][0]
                assert "sm.symbol = ANY(%s)" not in sql


class TestDashboardInsiderIntentEndpoint:
    """Tests for GET /api/dashboard/insider-intent"""

    def test_get_insider_intent(self, client, mock_db):
        """Test getting insider intent filings for dashboard."""
        mock_db.get_user_by_id.return_value = {"id": 1, "user_type": "regular"}
        mock_db.get_form144_filings_multi.return_value = {
            'filings': [
                {
                    'id': 1,
                    'symbol': 'AAPL',
                    'insider_name': 'Tim Cook',
                    'relationship': 'CEO',
                    'shares_to_sell': 50000,
                    'estimated_value': 9750000.0,
                    'filing_date': '2026-03-01',
                    'is_10b51_plan': False,
                },
            ],
            'total_count': 1,
        }

        with client.session_transaction() as sess:
            sess['user_id'] = 1

        with patch('app.deps.db', mock_db):
            response = client.get('/api/dashboard/insider-intent')
            assert response.status_code == 200
            data = response.get_json()
            assert 'insider_intent' in data
            assert len(data['insider_intent']['filings']) == 1
            assert data['insider_intent']['filings'][0]['symbol'] == 'AAPL'
            assert data['insider_intent']['total_count'] == 1

    def test_insider_intent_empty_watchlist(self, client, mock_db):
        """Test insider intent returns empty when user has no stocks."""
        mock_db.get_user_by_id.return_value = {"id": 1, "user_type": "regular"}
        mock_db.get_watchlist.return_value = []
        mock_db.get_user_portfolios.return_value = []

        with client.session_transaction() as sess:
            sess['user_id'] = 1

        with patch('app.deps.db', mock_db):
            response = client.get('/api/dashboard/insider-intent')
            assert response.status_code == 200
            data = response.get_json()
            assert data['insider_intent']['filings'] == []
            assert data['insider_intent']['total_count'] == 0
