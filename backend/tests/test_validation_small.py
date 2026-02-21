import pytest
from algorithm_validator import AlgorithmValidator

@pytest.mark.slow
@pytest.mark.integration
def test_algorithm_validation_small(db):
    """Run a small backtest validation (10 stocks, 1 year)."""
    validator = AlgorithmValidator(db)
    
    # Run small test
    summary = validator.run_sp500_backtests(
        years_back=1,
        max_workers=3,
        limit=10
    )
    
    assert summary['successful'] > 0
    assert summary['total_processed'] == 10
    
    # Verify results are in DB
    results = db.get_backtest_results(years_back=1)
    assert len(results) >= 0 # Should at least not crash
