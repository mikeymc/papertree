# ABOUTME: Tests for FIFO position tracking in trade history
# ABOUTME: Validates buy/sell matching, partial fills, open positions, and reasoning joins

import pytest
from datetime import datetime, timedelta


def insert_transaction(db, portfolio_id, symbol, tx_type, quantity, price, executed_at, note=None):
    """Insert a transaction with a specific timestamp for deterministic FIFO ordering."""
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


def link_decision(db, run_id, symbol, transaction_id, decision, reasoning, thesis_summary=None):
    """Create a strategy_decision linked to a transaction."""
    return db.create_strategy_decision(
        run_id=run_id,
        symbol=symbol,
        final_decision=decision,
        decision_reasoning=reasoning,
        thesis_summary=thesis_summary,
        transaction_id=transaction_id,
    )


class TestTradeHistoryFIFO:
    """Tests for FIFO position matching in get_portfolio_trade_history."""

    def test_simple_buy_sell_pair(self, test_db):
        """A single buy followed by a full sell produces one closed position."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 10, 10, 0, 0)

        insert_transaction(test_db, pid, "AAPL", "BUY", 10, 150.0, t0)
        insert_transaction(test_db, pid, "AAPL", "SELL", 10, 165.0, t0 + timedelta(days=30))

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 1
        t = trades[0]
        assert t["symbol"] == "AAPL"
        assert t["shares"] == 10
        assert t["entry_price"] == 150.0
        assert t["exit_price"] == 165.0
        assert t["status"] == "closed"
        assert t["return_pct"] == pytest.approx(10.0, abs=0.01)
        assert t["hold_days"] == 30

    def test_open_position(self, test_db):
        """A buy with no sell produces an open position."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 2, 1, 10, 0, 0)

        insert_transaction(test_db, pid, "MSFT", "BUY", 20, 400.0, t0)

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 1
        t = trades[0]
        assert t["symbol"] == "MSFT"
        assert t["shares"] == 20
        assert t["entry_price"] == 400.0
        assert t["exit_price"] is None
        assert t["exit_date"] is None
        assert t["status"] == "open"
        assert t["return_pct"] is None
        assert t["hold_days"] is None

    def test_partial_sell_splits_lot(self, test_db):
        """Selling fewer shares than a lot splits it into closed + open."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 5, 9, 0, 0)

        insert_transaction(test_db, pid, "GOOG", "BUY", 50, 100.0, t0)
        insert_transaction(test_db, pid, "GOOG", "SELL", 20, 120.0, t0 + timedelta(days=15))

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 2
        closed = [t for t in trades if t["status"] == "closed"]
        opened = [t for t in trades if t["status"] == "open"]
        assert len(closed) == 1
        assert len(opened) == 1
        assert closed[0]["shares"] == 20
        assert closed[0]["return_pct"] == pytest.approx(20.0, abs=0.01)
        assert opened[0]["shares"] == 30
        assert opened[0]["entry_price"] == 100.0

    def test_fifo_order_multiple_buys(self, test_db):
        """FIFO: first buy lot is consumed first when selling."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 1, 10, 0, 0)

        insert_transaction(test_db, pid, "TSLA", "BUY", 10, 200.0, t0)
        insert_transaction(test_db, pid, "TSLA", "BUY", 10, 250.0, t0 + timedelta(days=10))
        insert_transaction(test_db, pid, "TSLA", "SELL", 15, 300.0, t0 + timedelta(days=20))

        trades = test_db.get_portfolio_trade_history(pid)

        # Should produce: closed 10@200 (first lot fully consumed), closed 5@250 (partial),
        # open 5@250 (remainder)
        closed = sorted(
            [t for t in trades if t["status"] == "closed"],
            key=lambda t: t["entry_price"]
        )
        opened = [t for t in trades if t["status"] == "open"]

        assert len(closed) == 2
        assert len(opened) == 1

        # First lot: bought at 200, sold at 300
        assert closed[0]["shares"] == 10
        assert closed[0]["entry_price"] == 200.0
        assert closed[0]["exit_price"] == 300.0
        assert closed[0]["return_pct"] == pytest.approx(50.0, abs=0.01)

        # Second lot (partial): bought at 250, sold at 300
        assert closed[1]["shares"] == 5
        assert closed[1]["entry_price"] == 250.0
        assert closed[1]["exit_price"] == 300.0
        assert closed[1]["return_pct"] == pytest.approx(20.0, abs=0.01)

        # Remainder
        assert opened[0]["shares"] == 5
        assert opened[0]["entry_price"] == 250.0

    def test_multiple_symbols_independent(self, test_db):
        """FIFO matching is independent per symbol."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 1, 10, 0, 0)

        insert_transaction(test_db, pid, "AAPL", "BUY", 10, 150.0, t0)
        insert_transaction(test_db, pid, "MSFT", "BUY", 5, 400.0, t0)
        insert_transaction(test_db, pid, "AAPL", "SELL", 10, 160.0, t0 + timedelta(days=5))

        trades = test_db.get_portfolio_trade_history(pid)

        aapl = [t for t in trades if t["symbol"] == "AAPL"]
        msft = [t for t in trades if t["symbol"] == "MSFT"]

        assert len(aapl) == 1
        assert aapl[0]["status"] == "closed"
        assert len(msft) == 1
        assert msft[0]["status"] == "open"

    def test_strategy_reasoning_joined(self, test_db):
        """Strategy decision reasoning is joined to entry/exit trades."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        strategy_id = test_db.create_strategy(user_id, pid, "auto", conditions={"logic": "simple"})
        run_id = test_db.create_strategy_run(strategy_id)
        t0 = datetime(2026, 1, 10, 10, 0, 0)

        buy_id = insert_transaction(test_db, pid, "NVDA", "BUY", 10, 500.0, t0, note="Strategy buy")
        sell_id = insert_transaction(test_db, pid, "NVDA", "SELL", 10, 550.0, t0 + timedelta(days=20), note="Score dropped")

        link_decision(test_db, run_id, "NVDA", buy_id, "BUY", "Strong earnings growth", "AI leader")
        link_decision(test_db, run_id, "NVDA", sell_id, "SELL", "Score below threshold")

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 1
        t = trades[0]
        assert t["entry_note"] == "Strategy buy"
        assert t["exit_note"] == "Score dropped"
        assert t["entry_reasoning"] == "Strong earnings growth"
        assert t["exit_reasoning"] == "Score below threshold"

    def test_dividends_excluded(self, test_db):
        """DIVIDEND transactions should not be treated as buys or sells."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 10, 10, 0, 0)

        insert_transaction(test_db, pid, "AAPL", "BUY", 10, 150.0, t0)
        insert_transaction(test_db, pid, "AAPL", "DIVIDEND", 10, 0.5, t0 + timedelta(days=30))

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 1
        assert trades[0]["status"] == "open"
        assert trades[0]["shares"] == 10

    def test_sorted_most_recent_entry_first(self, test_db):
        """Results should be sorted with most recent entry first."""
        user_id = test_db.create_user("g1", "a@b.com", "Test", None)
        pid = test_db.create_portfolio(user_id, "Test")
        t0 = datetime(2026, 1, 1, 10, 0, 0)

        insert_transaction(test_db, pid, "AAPL", "BUY", 10, 150.0, t0)
        insert_transaction(test_db, pid, "GOOG", "BUY", 5, 100.0, t0 + timedelta(days=10))

        trades = test_db.get_portfolio_trade_history(pid)

        assert len(trades) == 2
        # Most recent entry first
        assert trades[0]["symbol"] == "GOOG"
        assert trades[1]["symbol"] == "AAPL"
