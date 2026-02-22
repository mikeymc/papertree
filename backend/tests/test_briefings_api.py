# ABOUTME: Tests for briefings API endpoints
# ABOUTME: Validates GET /api/portfolios/<id>/briefings and GET /api/briefings/<id>

import pytest
import json
from unittest.mock import patch, MagicMock


@pytest.fixture
def authenticated_client(test_client):
    """Test client with mocked authentication."""
    with test_client.session_transaction() as sess:
        sess['user_id'] = 1
    return test_client


@pytest.fixture
def seed_briefing_data(authenticated_client):
    """Seed the database with briefing test data via the app's db."""
    from app import db

    # Use high IDs (9900+) to avoid conflicts with other test fixtures
    _PID = 9901  # portfolio id
    _SID = 9901  # strategy id
    _RID = 9901  # run id
    _BID = 9901  # briefing id

    conn = db.get_connection()
    cursor = conn.cursor()

    # Clean up any existing data from prior runs
    cursor.execute("DELETE FROM strategy_briefings WHERE id = %s", (_BID,))
    cursor.execute("DELETE FROM strategy_runs WHERE id = %s", (_RID,))
    cursor.execute("DELETE FROM investment_strategies WHERE id = %s", (_SID,))
    cursor.execute("DELETE FROM portfolios WHERE id = %s", (_PID,))

    cursor.execute("""
        INSERT INTO users (id, email, name, google_id)
        VALUES (1, 'test@test.com', 'Test User', 'g1')
        ON CONFLICT (id) DO NOTHING
    """)
    cursor.execute("""
        INSERT INTO portfolios (id, user_id, name, initial_cash)
        VALUES (%s, 1, 'Briefing Test Portfolio', 100000.0)
    """, (_PID,))
    cursor.execute("""
        INSERT INTO investment_strategies (id, user_id, portfolio_id, name, conditions)
        VALUES (%s, 1, %s, 'Test Strategy', '{}')
    """, (_SID, _PID))
    cursor.execute("""
        INSERT INTO strategy_runs (id, strategy_id, status)
        VALUES (%s, %s, 'completed')
    """, (_RID, _SID))
    cursor.execute("""
        INSERT INTO strategy_briefings
        (id, run_id, strategy_id, portfolio_id, universe_size, candidates, qualifiers,
         theses, targets, trades, portfolio_value, portfolio_return_pct,
         spy_return_pct, alpha, buys_json, sells_json, holds_json, watchlist_json,
         executive_summary, generated_at)
        VALUES (%s, %s, %s, %s, 1000, 500, 25, 10, 5, 3, 102500.0, 2.5, 1.2, 1.3,
                '[]', '[]', '[]', '[]', 'Test summary.', NOW())
    """, (_BID, _RID, _SID, _PID))

    conn.commit()
    db.return_connection(conn)

    return authenticated_client


def test_get_portfolio_briefings(seed_briefing_data):
    """Test GET /api/portfolios/<id>/briefings returns briefings."""
    client = seed_briefing_data
    response = client.get('/api/portfolios/9901/briefings')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['candidates'] == 500
    assert data[0]['executive_summary'] == 'Test summary.'


def test_get_portfolio_briefings_empty(authenticated_client):
    """Test GET /api/portfolios/<id>/briefings returns empty list for no briefings."""
    response = authenticated_client.get('/api/portfolios/999/briefings')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []


def test_get_single_briefing(seed_briefing_data):
    """Test GET /api/briefings/<id> returns a single briefing."""
    client = seed_briefing_data
    response = client.get('/api/briefings/9901')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 9901
    assert data['executive_summary'] == 'Test summary.'


def test_get_single_briefing_not_found(authenticated_client):
    """Test GET /api/briefings/<id> returns 404 for non-existent briefing."""
    response = authenticated_client.get('/api/briefings/999')
    assert response.status_code == 404
