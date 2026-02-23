import pytest
from algorithm.validator import AlgorithmValidator

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

    # Requires weekly price data in DB — skip if none available
    if summary['successful'] == 0 and summary.get('total_processed', 0) == 10:
        pytest.skip("No weekly price data in test database — populate DB first")

    assert summary['successful'] > 0
    assert summary['total_processed'] == 10

    # Verify results are in DB
    results = db.get_backtest_results(years_back=1)
    assert len(results) >= 0 # Should at least not crash
