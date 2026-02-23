import pytest
from data_fetcher import DataFetcher

@pytest.mark.integration
def test_edgar_with_postgres(db):
    """Test EdgarFetcher with PostgreSQL backend."""
    # Initialize DataFetcher (which creates EdgarFetcher with db connection)
    fetcher = DataFetcher(db)
    
    # Test fetching Apple data (mocked or real based on env, but assuming real/cached here)
    fundamentals = fetcher.edgar_fetcher.fetch_stock_fundamentals("AAPL")
    
    assert fundamentals is not None, "Failed to fetch AAPL data"
    assert fundamentals.get('company_name') == "Apple Inc."
    assert fundamentals.get('cik') is not None
    assert len(fundamentals.get('eps_history', [])) > 0
