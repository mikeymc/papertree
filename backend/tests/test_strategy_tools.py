# ABOUTME: Tests for strategy management tool executors (get, list, update, activity, decisions)
# ABOUTME: Follows the same mock-DB pattern as test_portfolio_tools.py

import json
import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend')))

sys.modules["google.genai"] = MagicMock()
sys.modules["google.genai.types"] = MagicMock()
sys.modules["fred_service"] = MagicMock()
sys.modules["characters"] = MagicMock()

from database import Database
from agent_tools import ToolExecutor


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Database)
    return db


@pytest.fixture
def executor(mock_db):
    return ToolExecutor(mock_db)



# =========================================================================
# get_portfolio_strategy
# =========================================================================

def test_get_portfolio_strategy_success(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 1, 'strategy_id': 5}
    mock_db.get_strategy.return_value = {
        'id': 5, 'user_id': 1, 'name': 'My Strategy',
        'conditions': json.dumps({'filters': []}),
        'position_sizing': json.dumps({'method': 'equal_weight', 'max_position_pct': 5.0}),
        'exit_conditions': json.dumps({'profit_target_pct': 50}),
        'enabled': True,
    }

    result = executor._get_portfolio_strategy_config(portfolio_id=1, user_id=1)

    assert result['success'] is True
    assert result['strategy']['name'] == 'My Strategy'
    mock_db.get_strategy.assert_called_once_with(5)


def test_get_portfolio_strategy_not_found(executor, mock_db):
    mock_db.get_portfolio.return_value = None

    result = executor._get_portfolio_strategy_config(portfolio_id=999, user_id=1)

    assert result['success'] is False
    assert 'not found' in result['error'].lower()


def test_get_portfolio_strategy_unauthorized(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 2}

    result = executor._get_portfolio_strategy_config(portfolio_id=1, user_id=1)

    assert result['success'] is False
    assert 'unauthorized' in result['error'].lower()


# =========================================================================
# update_portfolio_strategy
# =========================================================================

def test_update_portfolio_strategy_name_only(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 1, 'strategy_id': 5}
    mock_db.get_strategy.return_value = {
        'id': 5, 'user_id': 1, 'name': 'Old Name',
        'position_sizing': {'method': 'equal_weight', 'max_position_pct': 5.0},
        'exit_conditions': {},
    }
    mock_db.update_strategy.return_value = True

    result = executor._update_portfolio_strategy(portfolio_id=1, user_id=1, name='New Name')

    assert result['success'] is True
    mock_db.update_strategy.assert_called_once_with(1, 5, name='New Name')


def test_update_portfolio_strategy_unauthorized(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 2}

    result = executor._update_portfolio_strategy(portfolio_id=1, user_id=1, name='Hacked')

    assert result['success'] is False
    assert 'unauthorized' in result['error'].lower()
    mock_db.update_strategy.assert_not_called()


def test_update_portfolio_strategy_position_sizing_merge(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 1, 'strategy_id': 5}
    mock_db.get_strategy.return_value = {
        'id': 5, 'user_id': 1, 'name': 'S',
        'position_sizing': {'method': 'equal_weight', 'max_position_pct': 5.0},
        'exit_conditions': {},
    }
    mock_db.update_strategy.return_value = True

    result = executor._update_portfolio_strategy(portfolio_id=1, user_id=1, max_position_pct=10.0)

    assert result['success'] is True
    call_kwargs = mock_db.update_strategy.call_args[1]
    assert call_kwargs['position_sizing']['method'] == 'equal_weight'
    assert call_kwargs['position_sizing']['max_position_pct'] == 10.0



# =========================================================================
# get_portfolio_strategy_activity
# =========================================================================

def test_get_portfolio_strategy_activity_success(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 1, 'strategy_id': 5}
    mock_db.get_strategy.return_value = {'id': 5, 'user_id': 1, 'name': 'S'}
    mock_db.get_strategy_runs.return_value = [
        {'id': 10, 'strategy_id': 5, 'started_at': '2026-02-10', 'status': 'success',
         'trades_executed': 3, 'stocks_screened': 100},
    ]
    mock_db.get_strategy_performance.return_value = [
        {'snapshot_date': '2026-02-10', 'portfolio_return_pct': 2.5, 'alpha': 1.1},
    ]

    result = executor._get_portfolio_strategy_activity(portfolio_id=1, user_id=1)

    assert result['success'] is True
    assert len(result['runs']) == 1
    mock_db.get_strategy_runs.assert_called_once_with(5, 5)  # default limit=5


def test_get_portfolio_strategy_activity_unauthorized(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 2}

    result = executor._get_portfolio_strategy_activity(portfolio_id=1, user_id=1)

    assert result['success'] is False
    assert 'unauthorized' in result['error'].lower()


# =========================================================================
# get_portfolio_strategy_decisions
# =========================================================================

SAMPLE_DECISIONS = [
    {'id': 1, 'symbol': 'AAPL', 'final_decision': 'BUY', 'lynch_score': 75.0,
     'buffett_score': 80.0, 'thesis_summary': 'Strong growth', 'shares_traded': 10},
    {'id': 2, 'symbol': 'MSFT', 'final_decision': 'SKIP', 'lynch_score': 55.0,
      'buffett_score': 60.0, 'thesis_summary': 'Too expensive', 'shares_traded': None},
    {'id': 3, 'symbol': 'TSLA', 'final_decision': 'SELL', 'lynch_score': 40.0,
      'buffett_score': 45.0, 'thesis_summary': 'Declining metrics', 'shares_traded': 5},
]


def test_get_portfolio_strategy_decisions_defaults_to_latest_run(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 1, 'strategy_id': 5}
    mock_db.get_strategy.return_value = {'id': 5, 'user_id': 1}
    mock_db.get_strategy_runs.return_value = [
        {'id': 42, 'strategy_id': 5, 'started_at': '2026-02-10'},
    ]
    mock_db.get_run_decisions.return_value = SAMPLE_DECISIONS

    result = executor._get_portfolio_strategy_decisions(portfolio_id=1, user_id=1)

    assert result['success'] is True
    mock_db.get_run_decisions.assert_called_once_with(42)  # latest run


def test_get_portfolio_strategy_decisions_unauthorized(executor, mock_db):
    mock_db.get_portfolio.return_value = {'id': 1, 'user_id': 2}

    result = executor._get_portfolio_strategy_decisions(portfolio_id=1, user_id=1)

    assert result['success'] is False
    assert 'unauthorized' in result['error'].lower()
