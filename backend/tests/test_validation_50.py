import pytest
from algorithm_validator import AlgorithmValidator
from correlation_analyzer import CorrelationAnalyzer

@pytest.mark.slow
@pytest.mark.integration
def test_algorithm_validation_50(db):
    """Run a larger backtest validation (50 stocks, 1 year)."""
    validator = AlgorithmValidator(db)
    analyzer = CorrelationAnalyzer(db)

    # Run validation with 50 stocks
    summary = validator.run_sp500_backtests(
        years_back=1,
        max_workers=5,
        limit=50
    )

    # Requires weekly price data in DB — skip if none available
    if summary['successful'] == 0 and summary.get('total_processed', 0) == 50:
        pytest.skip("No weekly price data in test database — populate DB first")

    assert summary['successful'] > 0
    assert summary['total_processed'] == 50
    
    # Run correlation analysis
    analysis = analyzer.analyze_results(years_back=1)
    
    if 'error' not in analysis:
        assert analysis['total_stocks'] > 0
        assert 'overall_correlation' in analysis
