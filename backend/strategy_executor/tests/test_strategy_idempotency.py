
import pytest
from unittest.mock import MagicMock, patch
import sys
import os


from strategy_executor import StrategyExecutor

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@pytest.fixture
def executor(mock_db):
    with patch('strategy_executor.PositionSizer'):
        exe = StrategyExecutor(mock_db)
        return exe

def test_execute_trades_idempotency_market_closed(executor, mock_db):
    """Test that duplicate alerts are not created when market is closed."""
    import portfolio_service
    from strategy_executor.models import PositionSize
    
    # Setup mocks
    portfolio_service.is_market_open.return_value = False
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 42}
    mock_db.get_portfolio_summary.return_value = {'cash': 10000, 'total_value': 10000}
    mock_db.get_portfolio_holdings.return_value = {}
    
    portfolio_id = 1
    user_id = 42
    run_id = 100
    
    strategy = {
        'id': 1,
        'portfolio_id': portfolio_id,
        'position_sizing': {'method': 'fixed_pct'}
    }
    
    # Existing alerts (idempotency base)
    mock_db.get_alerts.return_value = [
        {
            'id': 301,
            'symbol': 'AAPL',
            'action_type': 'market_buy',
            'status': 'active',
            'portfolio_id': portfolio_id
        }
    ]
    
    # Decisions: AAPL (duplicate) and GOOG (new)
    buy_decisions = [
        {'symbol': 'AAPL', 'consensus_score': 80, 'id': 201, 'position_type': 'new'},
        {'symbol': 'GOOG', 'consensus_score': 85, 'id': 202, 'position_type': 'new'}
    ]
    
    # Mock position sizing (shares > 0)
    pos1 = PositionSize(shares=10, estimated_value=1500.0, position_pct=1.5, reasoning="Test")
    pos2 = PositionSize(shares=5, estimated_value=2000.0, position_pct=2.0, reasoning="Test")
    
    executor.position_sizer.calculate_target_orders = MagicMock(return_value=([], [
        {'symbol': 'AAPL', 'position': pos1, 'decision': buy_decisions[0]},
        {'symbol': 'GOOG', 'position': pos2, 'decision': buy_decisions[1]}
    ]))
    
    # Run execution
    executor._execute_trades(
        buy_decisions=buy_decisions,
        exits=[],
        strategy=strategy,
        run_id=run_id
    )
    
    # Verify results
    # create_alert should only be called ONCE for GOOG (AAPL skipped as duplicate)
    assert mock_db.create_alert.call_count == 1
    args, kwargs = mock_db.create_alert.call_args
    assert kwargs['symbol'] == 'GOOG'
    assert kwargs['action_type'] == 'market_buy'

def test_execute_trades_idempotency_sells(executor, mock_db):
    """Test that duplicate sell alerts are not created when market is closed."""
    import portfolio_service
    from strategy_executor.models import ExitSignal
    
    portfolio_service.is_market_open.return_value = False
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 42}
    mock_db.get_portfolio_summary.return_value = {'cash': 10000, 'total_value': 10000}
    mock_db.get_portfolio_holdings.return_value = {'MSFT': 10}
    
    portfolio_id = 1
    user_id = 42
    run_id = 200
    
    strategy = {
        'id': 1,
        'portfolio_id': portfolio_id,
        'position_sizing': {'method': 'fixed_pct'}
    }
    
    # Existing sell alert
    mock_db.get_alerts.return_value = [
        {
            'id': 401,
            'symbol': 'MSFT',
            'action_type': 'market_sell',
            'status': 'active',
            'portfolio_id': portfolio_id
        }
    ]
    
    # Exits: MSFT (duplicate) and TSLA (new)
    exits = [
        ExitSignal(symbol='MSFT', quantity=10, reason="Test", current_value=3000.0),
        ExitSignal(symbol='TSLA', quantity=5, reason="Test", current_value=1000.0)
    ]
    
    # Mock position sizing to return no new buys
    executor.position_sizer.calculate_target_orders = MagicMock(return_value=([], []))
    
    # Run execution
    executor._execute_trades(
        buy_decisions=[],
        exits=exits,
        strategy=strategy,
        run_id=run_id
    )
    
    # Verify results
    # create_alert should only be called ONCE for TSLA
    assert mock_db.create_alert.call_count == 1
    args, kwargs = mock_db.create_alert.call_args
    assert kwargs['symbol'] == 'TSLA'
    assert kwargs['action_type'] == 'market_sell'
