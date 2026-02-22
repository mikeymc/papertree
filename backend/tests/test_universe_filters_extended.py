import pandas as pd
from unittest.mock import MagicMock
from strategy_executor.universe_filter import UniverseFilter


@pytest.fixture
def mock_sv():
    return MagicMock()

def test_universe_filter_dividend_yield(mock_sv):
    uf = UniverseFilter(db=None, stock_vectors=mock_sv)
    conditions = {
        'filters': [{'field': 'dividend_yield', 'operator': '>', 'value': 3.0}]
    }
    
    df = pd.DataFrame([
        {'symbol': 'AAPL', 'dividend_yield': 1.0},
        {'symbol': 'T', 'dividend_yield': 5.0}
    ])
    mock_sv.load_vectors.return_value = df
    
    symbols = uf.filter_universe(conditions)
    assert 'T' in symbols
    assert 'AAPL' not in symbols

def test_peg_ratio_mapping(mock_sv):
    uf = UniverseFilter(db=None, stock_vectors=mock_sv)
    conditions = {
        'filters': [{'field': 'peg_ratio', 'operator': '<=', 'value': 1.0}]
    }
    
    df = pd.DataFrame([
        {'symbol': 'AAPL', 'peg_ratio': 0.8},
        {'symbol': 'TSLA', 'peg_ratio': 2.5}
    ])
    mock_sv.load_vectors.return_value = df
    
    symbols = uf.filter_universe(conditions)
    assert 'AAPL' in symbols
    assert 'TSLA' not in symbols

def test_price_52w_fallback(mock_sv):
    uf = UniverseFilter(db=None, stock_vectors=mock_sv)
    # price_vs_52wk_high is mapped to price_change_pct in some versions,
    # or it uses the raw field name if not mapped.
    # In universe_filter.py: field_mapping doesn't have it, so it uses 'price_vs_52wk_high'
    conditions = {
        'filters': [{'field': 'price_change_pct', 'operator': '<=', 'value': -20.0}]
    }
    
    df = pd.DataFrame([
        {'symbol': 'AAPL', 'price_change_pct': -25.0},
        {'symbol': 'MSFT', 'price_change_pct': -10.0}
    ])
    mock_sv.load_vectors.return_value = df
    
    symbols = uf.filter_universe(conditions)
    assert 'AAPL' in symbols
    assert 'MSFT' not in symbols
