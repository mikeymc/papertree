import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from strategy_executor.core import StrategyExecutorCore
from strategy_executor.models import ExitSignal

def test_universe_exit_logic():
    """Verify that held stocks failing filters are sold, and limit doesn't break it."""
    
    # Mock DB
    db = MagicMock()
    strategy = {
        'id': 1,
        'name': 'Test Strategy',
        'portfolio_id': 100,
        'enabled': True,
        'conditions': {'filters': []}
    }
    db.get_strategy.return_value = strategy
    db.create_strategy_run.return_value = 1001
    db.get_portfolio_summary.return_value = {'total_value': 10000, 'cash': 5000}
    
    # Portfolio has AAPL and MSFT
    db.get_portfolio_holdings.return_value = {'AAPL': 10, 'MSFT': 20}
    
    # Mock UniverseFilter
    executor = StrategyExecutorCore(db)
    executor.universe_filter = MagicMock()
    
    # Mock and wrap check_universe_compliance to inspect calls while keeping logic
    executor.exit_checker.check_universe_compliance = MagicMock(side_effect=executor.exit_checker.check_universe_compliance)
    
    # SCENARIO 1: AAPL passes, MSFT fails (dividend filter added)
    # limit = 10 (higher than candidates)
    executor.universe_filter.filter_universe.return_value = ['AAPL', 'GOOG']
    
    with patch.object(executor, '_score_candidates', return_value=([], [])):
        with patch.object(executor, '_generate_theses', return_value=[]):
            with patch.object(executor, '_deliberate', return_value=([], [], [])):
                with patch.object(executor, '_execute_trades', return_value=0):
                    with patch.object(executor, '_build_scorer', return_value=lambda x: {}):
                        with patch.object(executor.benchmark_tracker, 'record_strategy_performance', return_value={}):
                            with patch.object(db, 'save_briefing'):
                                with patch('strategy_executor.core.get_spy_price', return_value=500):
                                    print("Running Scenario 1: MSFT should be sold (fails filter), AAPL should be held.")
                                    executor.execute_strategy(strategy_id=1, limit=10)
                        
                        # Verify exit detection was called with the right data
                        # We need to peek into what was passed to check_universe_compliance
                        args, kwargs = executor.exit_checker.check_universe_compliance.call_args
                        held_symbols = args[0]
                        filtered_candidates = args[1]
                        
                        assert 'MSFT' in held_symbols
                        assert 'AAPL' in held_symbols
                        assert 'AAPL' in filtered_candidates
                        assert 'MSFT' not in filtered_candidates
                        print("  ✓ Scenario 1 passed: MSFT identified as exit.")

    # SCENARIO 2: AAPL and MSFT both pass, but limit = 1
    # MSFT should NOT be sold just because it was truncated from the scoring candidates
    db.get_portfolio_holdings.return_value = {'AAPL': 10, 'MSFT': 20}
    executor.universe_filter.filter_universe.return_value = ['AAPL', 'MSFT', 'GOOG']
    
    executor.exit_checker.check_universe_compliance.reset_mock()
    
    with patch.object(executor, '_score_candidates', return_value=([], [])):
        with patch.object(executor, '_generate_theses', return_value=[]):
            with patch.object(executor, '_deliberate', return_value=([], [], [])):
                with patch.object(executor, '_execute_trades', return_value=0):
                    with patch.object(executor, '_build_scorer', return_value=lambda x: {}):
                        with patch.object(executor.benchmark_tracker, 'record_strategy_performance', return_value={}):
                            with patch.object(db, 'save_briefing'):
                                with patch('strategy_executor.core.get_spy_price', return_value=500):
                                    print("\nRunning Scenario 2: Limit=1. MSFT truncated from candidates, but should NOT be sold.")
                                    # MSFT will be at index 1, so if limit=1, it will be truncated from filtered_candidates
                                    executor.execute_strategy(strategy_id=1, limit=1)
                        
                        args, kwargs = executor.exit_checker.check_universe_compliance.call_args
                        held_symbols = args[0]
                        all_passing_symbols = args[1]
                        
                        assert 'MSFT' in held_symbols
                        assert 'MSFT' in all_passing_symbols # This is the fix! It uses all_passing, not filtered_candidates
                        print("  ✓ Scenario 2 passed: MSFT retained despite limit=1.")

if __name__ == "__main__":
    try:
        test_universe_exit_logic()
        print("\nAll verification scenarios passed!")
    except AssertionError as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
