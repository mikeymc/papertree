# ABOUTME: Unit tests for the three-phase trade execution methods
# ABOUTME: Tests _process_exits, _calculate_all_positions, and _execute_buys independently

import pytest
from unittest.mock import MagicMock, patch, call
import sys
import os


# Pre-mock transitive deps needed to import strategy_executor
_MOCKED_MODULES = [
    "google.genai", "google.genai.types",
    "price_history_fetcher", "sec_data_fetcher", "news_fetcher",
    "material_events_fetcher", "sec_rate_limiter", "yfinance.cache",
]
_saved = {m: sys.modules.get(m) for m in _MOCKED_MODULES}
for m in _MOCKED_MODULES:
    sys.modules[m] = MagicMock()

from strategy_executor import StrategyExecutor
from strategy_executor.models import ExitSignal
from strategy_executor.position_sizing import PositionSizer
from strategy_executor.models import PositionSize

# Restore original modules to prevent cross-test contamination
for m in _MOCKED_MODULES:
    if _saved[m] is not None:
        sys.modules[m] = _saved[m]
    else:
        sys.modules.pop(m, None)


@pytest.fixture(autouse=True)
def mock_portfolio_service():
    """Localize portfolio_service mock to prevent leakage."""
    with patch.dict('sys.modules', {'portfolio_service': MagicMock()}):
        yield


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.get_portfolio_summary.return_value = {'cash': 10000.0, 'total_value': 50000.0}
    db.get_portfolio.return_value = {'user_id': 42}
    db.get_alerts.return_value = []
    return db


@pytest.fixture
def executor(mock_db):
    with patch('strategy_executor.PositionSizer'):
        exe = StrategyExecutor(mock_db)
        return exe


def make_exit(symbol, quantity=10, current_value=1000.0):
    return ExitSignal(symbol=symbol, quantity=quantity, reason='Test reason',
                      current_value=current_value, gain_pct=5.0)


def test_process_exits_resolves_price_when_current_value_none(executor):
    """When current_value is None, price is fetched and quantity * price is used as proceeds."""
    import portfolio_service
    portfolio_service.execute_trade.return_value = {'success': True}

    exit_signal = ExitSignal(symbol='AAPL', quantity=5, reason='Test',
                             current_value=None, gain_pct=None)
    executor.position_sizer._fetch_price = MagicMock(return_value=100.0)

    count, proceeds = executor._process_exits(
        exits=[exit_signal],
        portfolio_id=1,
        is_market_open=True,
        user_id=42,
        existing_alerts=[],
        run_id=1
    )

    executor.position_sizer._fetch_price.assert_called_once_with('AAPL')
    assert proceeds == 500.0


# ---------------------------------------------------------------------------
# _process_exits tests
# ---------------------------------------------------------------------------

def test_process_exits_market_open(executor, mock_db):
    """Market open: sells execute via execute_trade, returns (count, proceeds)."""
    import portfolio_service
    portfolio_service.execute_trade.reset_mock()
    portfolio_service.execute_trade.return_value = {'success': True}

    exits = [make_exit('AAPL', quantity=5, current_value=750.0),
              make_exit('TSLA', quantity=10, current_value=2000.0)]

    count, proceeds = executor._process_exits(
        exits=exits,
        portfolio_id=1,
        is_market_open=True,
        user_id=42,
        existing_alerts=[],
        run_id=1
    )

    assert count == 2
    assert proceeds == 2750.0
    assert portfolio_service.execute_trade.call_count == 2


def test_process_exits_market_closed(executor, mock_db):
    """Market closed: creates sell alerts, returns (count, anticipated_proceeds)."""
    mock_db.create_alert.side_effect = [101, 102]

    exits = [make_exit('AAPL', quantity=5, current_value=750.0),
              make_exit('TSLA', quantity=10, current_value=2000.0)]

    count, proceeds = executor._process_exits(
        exits=exits,
        portfolio_id=1,
        is_market_open=False,
        user_id=42,
        existing_alerts=[],
        run_id=1
    )

    assert count == 2
    assert proceeds == 2750.0
    assert mock_db.create_alert.call_count == 2
    # Verify it created market_sell alerts
    call_kwargs = [c.kwargs for c in mock_db.create_alert.call_args_list]
    assert all(kw['action_type'] == 'market_sell' for kw in call_kwargs)


def test_process_exits_skips_duplicates(executor, mock_db):
    """Idempotency: already-queued sell alerts are skipped."""
    existing_alerts = [
        {'symbol': 'AAPL', 'action_type': 'market_sell', 'portfolio_id': 1}
    ]
    exits = [make_exit('AAPL'), make_exit('TSLA')]
    mock_db.create_alert.return_value = 101

    count, proceeds = executor._process_exits(
        exits=exits,
        portfolio_id=1,
        is_market_open=False,
        user_id=42,
        existing_alerts=existing_alerts,
        run_id=1
    )

    # Only TSLA should be queued
    assert mock_db.create_alert.call_count == 1
    assert mock_db.create_alert.call_args.kwargs['symbol'] == 'TSLA'
    # But count still includes the duplicate (was already queued)
    assert count == 2


# ---------------------------------------------------------------------------
# _execute_buys tests
# ---------------------------------------------------------------------------

def _make_position(shares=10, estimated_value=1500.0):
    pos = MagicMock()
    pos.shares = shares
    pos.estimated_value = estimated_value
    pos.position_pct = 1.5
    pos.reasoning = 'Test'
    return pos


def test_execute_buys_market_open(executor, mock_db):
    """Market open: buys execute via execute_trade, decision records updated."""
    import portfolio_service
    portfolio_service.execute_trade.reset_mock()
    portfolio_service.execute_trade.return_value = {'success': True, 'transaction_id': 999}

    prioritized = [
        {'symbol': 'MSFT', 'decision': {'id': 10, 'position_type': 'new', 'consensus_reasoning': ''},
         'position': _make_position(shares=5, estimated_value=1000.0)},
    ]

    count = executor._execute_buys(
        prioritized_positions=prioritized,
        portfolio_id=1,
        is_market_open=True,
        user_id=42,
        existing_alerts=[],
        run_id=1
    )

    assert count == 1
    portfolio_service.execute_trade.assert_called_once()
    mock_db.update_strategy_decision.assert_called_once()


def test_execute_buys_market_closed(executor, mock_db):
    """Market closed: creates buy alerts, skips duplicates."""
    mock_db.create_alert.side_effect = [201, 202]

    # AAPL already queued, GOOG is new
    existing_alerts = [
        {'symbol': 'AAPL', 'action_type': 'market_buy', 'portfolio_id': 1}
    ]

    prioritized = [
        {'symbol': 'AAPL', 'decision': {'id': 11, 'position_type': 'new', 'consensus_reasoning': ''},
         'position': _make_position(shares=10, estimated_value=1500.0)},
        {'symbol': 'GOOG', 'decision': {'id': 12, 'position_type': 'new', 'consensus_reasoning': ''},
         'position': _make_position(shares=5, estimated_value=2000.0)},
    ]

    count = executor._execute_buys(
        prioritized_positions=prioritized,
        portfolio_id=1,
        is_market_open=False,
        user_id=42,
        existing_alerts=existing_alerts,
        run_id=1
    )

    # Both count (one duplicate, one new)
    assert count == 2
    # Only one alert created (GOOG)
    assert mock_db.create_alert.call_count == 1
    assert mock_db.create_alert.call_args.kwargs['symbol'] == 'GOOG'


# ---------------------------------------------------------------------------
# _execute_trades integration: cash anticipation
# ---------------------------------------------------------------------------

def test_execute_trades_uses_anticipated_cash(executor, mock_db):
    """When market closed, position sizing uses db_cash + anticipated_proceeds and excludes exited holdings."""
    import portfolio_service
    portfolio_service.is_market_open.return_value = False

    # DB cash is 5000, we will sell 2000 worth of stock off-hours
    mock_db.get_portfolio_summary.return_value = {'cash': 5000.0, 'total_value': 20000.0}
    mock_db.create_alert.return_value = 999
    mock_db.get_portfolio_holdings.return_value = {'TSLA': 10, 'MSFT': 5}
    mock_db.get_prices_batch.return_value = {'MSFT': 200.0}

    exits = [make_exit('TSLA', quantity=10, current_value=2000.0)]
    buy_decisions = [{'symbol': 'MSFT', 'consensus_score': 80, 'id': 300, 'position_type': 'new'}]

    captured = {}

    original_calc = executor.position_sizer.calculate_target_orders

    def spy_calc(**kwargs):
        captured['cash_available'] = kwargs.get('cash_available')
        captured['holdings'] = kwargs.get('holdings')
        return [], []

    executor.position_sizer.calculate_target_orders = spy_calc

    strategy = {
        'portfolio_id': 1,
        'position_sizing': {'method': 'equal_weight'}
    }

    executor._execute_trades(
        buy_decisions=buy_decisions,
        exits=exits,
        strategy=strategy,
        run_id=1
    )

    # Should be db_cash (5000) + anticipated_proceeds (2000) = 7000
    assert captured['cash_available'] == 7000.0
    # TSLA was exited, should not appear in holdings
    assert 'TSLA' not in captured['holdings']


# ---------------------------------------------------------------------------
# Deliberation exit tests
# ---------------------------------------------------------------------------

def test_deliberation_exits_on_held_positions(executor, mock_db):
    """AVOID verdict on a held position produces an ExitSignal."""
    held_symbols = {'AAPL'}
    mock_db.create_strategy_decision.return_value = 1

    # A held stock that gets AVOID
    enriched = [
        {
            'symbol': 'AAPL',
            'lynch_thesis': 'Some thesis',
            'buffett_thesis': 'Some thesis',
            'lynch_thesis_verdict': 'AVOID',
            'buffett_thesis_verdict': 'AVOID',
            'lynch_score': 40,
            'lynch_status': 'poor',
            'buffett_score': 35,
            'buffett_status': 'poor',
        }
    ]

    with patch.object(executor, '_conduct_deliberation', return_value=('Avoid text', 'AVOID')):
        buy_decisions, deliberation_exits, held_verdicts = executor._deliberate(
            enriched=enriched,
            run_id=1,
            conditions={},
            held_symbols=held_symbols
        )

    assert len(buy_decisions) == 0
    assert len(deliberation_exits) == 1
    assert deliberation_exits[0].symbol == 'AAPL'
    assert 'AVOID' in deliberation_exits[0].reason


def test_deliberation_watch_does_not_exit(executor, mock_db):
    """WATCH verdict on a held position produces no ExitSignal."""
    held_symbols = {'AAPL'}
    mock_db.create_strategy_decision.return_value = 1

    enriched = [
        {
            'symbol': 'AAPL',
            'lynch_thesis': 'Some thesis',
            'buffett_thesis': 'Some thesis',
            'lynch_thesis_verdict': 'WATCH',
            'buffett_thesis_verdict': 'WATCH',
            'lynch_score': 60,
            'lynch_status': 'ok',
            'buffett_score': 55,
            'buffett_status': 'ok',
        }
    ]

    with patch.object(executor, '_conduct_deliberation', return_value=('Watch text', 'WATCH')):
        buy_decisions, deliberation_exits, held_verdicts = executor._deliberate(
            enriched=enriched,
            run_id=1,
            conditions={},
            held_symbols=held_symbols
        )

    assert len(deliberation_exits) == 0


def test_deliberate_watch_populates_held_verdicts(executor, mock_db):
    """WATCH verdict on a held position captures the stock's scores in held_verdicts."""
    held_symbols = {'AAPL'}
    mock_db.create_strategy_decision.return_value = 1

    # At least one thesis must be BUY to avoid short-circuit path
    enriched = [
        {
            'symbol': 'AAPL',
            'lynch_thesis': 'Some thesis',
            'buffett_thesis': 'Some thesis',
            'lynch_thesis_verdict': 'BUY',
            'buffett_thesis_verdict': 'WATCH',
            'lynch_score': 60,
            'lynch_status': 'ok',
            'buffett_score': 55,
            'buffett_status': 'ok',
        }
    ]

    with patch.object(executor, '_conduct_deliberation', return_value=('Watch text', 'WATCH')):
        buy_decisions, deliberation_exits, held_verdicts = executor._deliberate(
            enriched=enriched,
            run_id=1,
            conditions={},
            held_symbols=held_symbols
        )

    assert len(held_verdicts) == 1
    assert held_verdicts[0]['symbol'] == 'AAPL'
    assert held_verdicts[0]['lynch_score'] == 60
    assert held_verdicts[0]['buffett_score'] == 55
    assert held_verdicts[0]['final_verdict'] == 'WATCH'


def test_execute_trades_includes_held_verdicts_as_candidates(executor, mock_db):
    """held_verdicts are included in the candidates list for position sizing."""
    import portfolio_service
    portfolio_service.is_market_open.return_value = False

    mock_db.get_portfolio_summary.return_value = {'cash': 0.0, 'total_value': 10000.0}
    mock_db.get_portfolio_holdings.return_value = {'AAPL': 20}
    mock_db.create_alert.return_value = 999
    mock_db.get_prices_batch.return_value = {'AAPL': 100.0, 'MSFT': 200.0}

    held_verdicts = [
        {'symbol': 'AAPL', 'lynch_score': 70, 'buffett_score': 70, 'final_verdict': 'WATCH'}
    ]
    buy_decisions = [{'symbol': 'MSFT', 'consensus_score': 70, 'id': 1,
                      'position_type': 'new', 'consensus_reasoning': ''}]

    captured = {}

    def spy_calc(**kwargs):
        captured['candidates'] = kwargs.get('candidates')
        return [], []

    executor.position_sizer.calculate_target_orders = spy_calc

    strategy = {
        'portfolio_id': 1,
        'position_sizing': {'method': 'equal_weight'}
    }

    executor._execute_trades(
        buy_decisions=buy_decisions,
        exits=[],
        strategy=strategy,
        run_id=1,
        held_verdicts=held_verdicts
    )

    candidate_symbols = {c['symbol'] for c in captured['candidates']}
    assert 'AAPL' in candidate_symbols, "held_verdicts AAPL should be in candidates"
    assert 'MSFT' in candidate_symbols, "buy_decisions MSFT should be in candidates"
