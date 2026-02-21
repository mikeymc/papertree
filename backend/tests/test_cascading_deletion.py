# Tests for cascading deletion of portfolios and strategies

import pytest
from datetime import date, datetime

def test_cascading_deletion(test_db):
    """Test that deleting a portfolio cascades to all associated data."""
    # 1. Setup Data
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    # Clean up any existing test user to ensure a fresh start
    cursor.execute("DELETE FROM users WHERE email = 'cascade_test@example.com'")
    conn.commit()

    user_id = test_db.create_user("google_cascade", "cascade_test@example.com", "Cascade User", None)
    
    # Create the stock record to satisfy foreign key constraints for alerts
    cursor.execute("INSERT INTO stocks (symbol, company_name) VALUES ('AAPL', 'Apple Inc.') ON CONFLICT (symbol) DO NOTHING")
    conn.commit()
    
    portfolio_id = test_db.create_portfolio(user_id, "Cascade Test Portfolio")
    
    # Associate a strategy
    strategy_id = test_db.create_strategy(
        user_id, portfolio_id, "Cascade Strategy", 
        conditions={"logic": "simple"},
        consensus_mode="both_agree"
    )

    # Record a transaction
    tx_id = test_db.record_transaction(portfolio_id, "AAPL", "BUY", 10, 150.0)

    # Save a snapshot
    test_db.save_portfolio_snapshot(portfolio_id, 100000.0, 98500.0, 1500.0)

    # Create an alert
    cursor.execute("""
        INSERT INTO alerts (user_id, symbol, condition_type, condition_params, portfolio_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (user_id, "AAPL", "price_below", '{"price": 100.0}', portfolio_id))
    alert_id = cursor.fetchone()[0]
    conn.commit()

    # Create a strategy run
    run_id = test_db.create_strategy_run(strategy_id)

    # Create a decision
    test_db.create_strategy_decision(run_id, "AAPL", lynch_score=80.0, final_decision="BUY", transaction_id=tx_id)

    # Create performance record
    test_db.save_strategy_performance(strategy_id, date.today(), 100000.0)

    # Create a briefing
    cursor.execute("""
        INSERT INTO strategy_briefings (run_id, strategy_id, portfolio_id, executive_summary)
        VALUES (%s, %s, %s, %s)
    """, (run_id, strategy_id, portfolio_id, "Test Summary"))
    conn.commit()

    # 2. Verify everything exists
    cursor.execute("SELECT COUNT(*) FROM portfolios WHERE id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM investment_strategies WHERE id = %s", (strategy_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM portfolio_transactions WHERE portfolio_id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM portfolio_value_snapshots WHERE portfolio_id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE id = %s", (alert_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM strategy_runs WHERE id = %s", (run_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM strategy_decisions WHERE run_id = %s", (run_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM strategy_performance WHERE strategy_id = %s", (strategy_id,))
    assert cursor.fetchone()[0] == 1
    cursor.execute("SELECT COUNT(*) FROM strategy_briefings WHERE run_id = %s", (run_id,))
    assert cursor.fetchone()[0] == 1

    # Return connection to avoid leaks
    test_db.return_connection(conn)

    # 3. Execution - Delete Portfolio
    test_db.delete_portfolio(portfolio_id, user_id)

    # 4. Validation - Everything should be gone
    conn = test_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM portfolios WHERE id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM investment_strategies WHERE id = %s", (strategy_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM portfolio_transactions WHERE portfolio_id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM portfolio_value_snapshots WHERE portfolio_id = %s", (portfolio_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE id = %s", (alert_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM strategy_runs WHERE id = %s", (run_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM strategy_decisions WHERE run_id = %s", (run_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM strategy_performance WHERE strategy_id = %s", (strategy_id,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM strategy_briefings WHERE run_id = %s", (run_id,))
    assert cursor.fetchone()[0] == 0
