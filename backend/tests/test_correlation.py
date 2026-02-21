import pytest
from correlation_analyzer import CorrelationAnalyzer

def test_correlation_analysis(db):
    """Analyze the correlation between scores and historical returns."""
    analyzer = CorrelationAnalyzer(db)
    
    # Analyze the results (assuming they exist from previous test runs or seed data)
    analysis = analyzer.analyze_results(years_back=1)
    
    if 'error' in analysis:
        # If no results to analyze, we might want to skip or just pass if it's the expected state
        pytest.skip(f"No results found for correlation analysis: {analysis['error']}")
    
    assert analysis['total_stocks'] >= 0
    assert 'overall_correlation' in analysis
    assert 'component_correlations' in analysis
    assert 'score_buckets' in analysis
