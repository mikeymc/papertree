# ABOUTME: Tests for the trade history API endpoint
# ABOUTME: Validates GET /api/portfolios/<id>/trade-history returns FIFO positions

import pytest
import json
from datetime import datetime, timedelta

from app import app


@pytest.fixture
def client(test_db, monkeypatch):
    """Flask test client with test database"""
    import app as app_module
    import auth

    monkeypatch.setattr(app_module.deps, 'db', test_db)
    monkeypatch.setattr(auth, 'DEV_AUTH_BYPASS', False)

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client, test_db):
    """Authenticated client with test user"""
    user_id = test_db.create_user("google_123", "test@example.com", "Test User", None)
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
    return client, user_id


def insert_transaction(db, portfolio_id, symbol, tx_type, quantity, price, executed_at, note=None):
    """Insert a transaction with a specific timestamp."""
    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        total_value = quantity * price
        cursor.execute("""
            INSERT INTO portfolio_transactions
            (portfolio_id, symbol, transaction_type, quantity, price_per_share, total_value, executed_at, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (portfolio_id, symbol, tx_type, quantity, price, total_value, executed_at, note))
        tx_id = cursor.fetchone()[0]
        conn.commit()
        return tx_id
    finally:
        db.return_connection(conn)


class TestTradeHistoryEndpoint:
    """Tests for GET /api/portfolios/<id>/trade-history"""

    def test_requires_auth(self, client):
        response = client.get('/api/portfolios/1/trade-history')
        assert response.status_code == 401

    def test_not_found_for_other_user(self, auth_client, test_db):
        client, user_id = auth_client
        other_id = test_db.create_user("other", "other@b.com", "Other", None)
        pid = test_db.create_portfolio(other_id, "Other Portfolio")

        response = client.get(f'/api/portfolios/{pid}/trade-history')
        assert response.status_code == 404

    def test_returns_trades(self, auth_client, test_db):
        client, user_id = auth_client
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 10, 10, 0, 0)

        insert_transaction(test_db, pid, "AAPL", "BUY", 10, 150.0, t0)
        insert_transaction(test_db, pid, "AAPL", "SELL", 10, 165.0, t0 + timedelta(days=30))

        response = client.get(f'/api/portfolios/{pid}/trade-history')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "trades" in data
        assert len(data["trades"]) == 1
        assert data["trades"][0]["symbol"] == "AAPL"
        assert data["trades"][0]["status"] == "closed"
        assert data["trades"][0]["return_pct"] == pytest.approx(10.0, abs=0.01)

    def test_empty_portfolio(self, auth_client, test_db):
        client, user_id = auth_client
        pid = test_db.create_portfolio(user_id, "Empty")

        response = client.get(f'/api/portfolios/{pid}/trade-history')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["trades"] == []
