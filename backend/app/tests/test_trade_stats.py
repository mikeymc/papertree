# ABOUTME: Tests for the portfolio trade statistics endpoint
# ABOUTME: Validates win rate, best/worst trade, and hold duration calculations

import pytest
from unittest.mock import patch, MagicMock


class TestTradeStatsEndpoint:
    """Tests for GET /api/portfolios/<id>/trade-stats."""

    @pytest.fixture
    def client(self, test_database):
        import os, sys
        os.environ['DB_NAME'] = test_database
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_USER'] = 'lynch'
        os.environ['DB_PASSWORD'] = 'lynch_dev_password'
        os.environ['DEV_AUTH_BYPASS'] = '1'

        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        sys.path.insert(0, os.path.abspath(backend_path))

        from app import app
        app.config['TESTING'] = True

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            yield client

    def test_returns_trade_stats_for_owned_portfolio(self, client):
        with patch('app.portfolios.deps') as mock_deps:
            mock_deps.db.get_portfolio.return_value = {'id': 1, 'user_id': 1}
            mock_deps.db.get_portfolio_trade_stats.return_value = {
                'total_trades': 10,
                'winning_trades': 7,
                'losing_trades': 3,
                'win_rate': 70.0,
                'best_trade': {'symbol': 'AAPL', 'return_pct': 42.5},
                'worst_trade': {'symbol': 'TSLA', 'return_pct': -18.2},
                'avg_hold_days': 45.0
            }

            response = client.get('/api/portfolios/1/trade-stats')

            assert response.status_code == 200
            data = response.get_json()
            assert data['total_trades'] == 10
            assert data['win_rate'] == 70.0
            assert data['best_trade']['symbol'] == 'AAPL'

    def test_returns_404_for_missing_portfolio(self, client):
        with patch('app.portfolios.deps') as mock_deps:
            mock_deps.db.get_portfolio.return_value = None

            response = client.get('/api/portfolios/999/trade-stats')
            assert response.status_code == 404

    def test_returns_zeros_for_empty_portfolio(self, client):
        with patch('app.portfolios.deps') as mock_deps:
            mock_deps.db.get_portfolio.return_value = {'id': 1, 'user_id': 1}
            mock_deps.db.get_portfolio_trade_stats.return_value = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'best_trade': None,
                'worst_trade': None,
                'avg_hold_days': 0.0
            }

            response = client.get('/api/portfolios/1/trade-stats')
            assert response.status_code == 200
            data = response.get_json()
            assert data['total_trades'] == 0
            assert data['best_trade'] is None


class TestPortfolioTradeStatsQuery:
    """Tests for the database trade stats query."""

    def test_win_rate_calculation(self, test_db):
        """Win rate = winning_trades / total_trades * 100."""
        # Create a user and portfolio
        conn = test_db.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (email, name, is_verified)
            VALUES ('test@example.com', 'Test', true)
            RETURNING id
        """)
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO portfolios (user_id, name, initial_cash)
            VALUES (%s, 'Test Portfolio', 100000)
            RETURNING id
        """, (user_id,))
        portfolio_id = cursor.fetchone()[0]

        # Insert a winning trade pair (BUY at 100, SELL at 150)
        cursor.execute("""
            INSERT INTO portfolio_transactions (portfolio_id, symbol, transaction_type, quantity, price_per_share, total_value)
            VALUES (%s, 'AAPL', 'BUY', 10, 100.0, 1000.0)
        """, (portfolio_id,))

        cursor.execute("""
            INSERT INTO portfolio_transactions (portfolio_id, symbol, transaction_type, quantity, price_per_share, total_value)
            VALUES (%s, 'AAPL', 'SELL', 10, 150.0, 1500.0)
        """, (portfolio_id,))

        # Insert a losing trade pair (BUY at 200, SELL at 160)
        cursor.execute("""
            INSERT INTO portfolio_transactions (portfolio_id, symbol, transaction_type, quantity, price_per_share, total_value)
            VALUES (%s, 'TSLA', 'BUY', 5, 200.0, 1000.0)
        """, (portfolio_id,))

        cursor.execute("""
            INSERT INTO portfolio_transactions (portfolio_id, symbol, transaction_type, quantity, price_per_share, total_value)
            VALUES (%s, 'TSLA', 'SELL', 5, 160.0, 800.0)
        """, (portfolio_id,))

        conn.commit()
        cursor.close()
        test_db.return_connection(conn)

        stats = test_db.get_portfolio_trade_stats(portfolio_id)

        assert stats['total_trades'] == 2
        assert stats['winning_trades'] == 1
        assert stats['losing_trades'] == 1
        assert stats['win_rate'] == 50.0
        assert stats['best_trade']['symbol'] == 'AAPL'
        assert stats['worst_trade']['symbol'] == 'TSLA'
