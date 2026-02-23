# ABOUTME: Tests for vectorized scoring parity with scalar evaluate_stock
# ABOUTME: Ensures evaluate_batch produces identical scores to the existing single-stock evaluation

import pytest
import sys
import os

# sys.path is handled by backend/tests/conftest.py

from database import Database
from earnings_analyzer import EarningsAnalyzer
from scoring import LynchCriteria
from scoring.vectors import StockVectors, DEFAULT_ALGORITHM_CONFIG


def _seed_stock_data(db):
    """Insert test stocks with metrics and earnings history into the test database."""
    stocks = [
        ("AAPL", "Apple Inc.", "NASDAQ", "Technology", "US"),
        ("MSFT", "Microsoft Corp.", "NASDAQ", "Technology", "US"),
        ("JNJ", "Johnson & Johnson", "NYSE", "Healthcare", "US"),
    ]
    for symbol, name, exchange, sector, country in stocks:
        db.save_stock_basic(symbol, name, exchange, sector, country)
    db.flush()

    metrics = {
        "AAPL": {"price": 180.0, "market_cap": 2800000000000, "pe_ratio": 30.0,
                 "debt_to_equity": 1.5, "institutional_ownership": 0.60,
                 "dividend_yield": 0.5, "total_debt": 110000000000,
                 "gross_margin": 44.0, "price_change_pct": 2.5},
        "MSFT": {"price": 380.0, "market_cap": 2800000000000, "pe_ratio": 35.0,
                 "debt_to_equity": 0.4, "institutional_ownership": 0.72,
                 "dividend_yield": 0.7, "total_debt": 60000000000,
                 "gross_margin": 69.0, "price_change_pct": 1.8},
        "JNJ": {"price": 160.0, "market_cap": 400000000000, "pe_ratio": 16.0,
                "debt_to_equity": 0.5, "institutional_ownership": 0.70,
                "dividend_yield": 2.9, "total_debt": 30000000000,
                "gross_margin": 68.0, "price_change_pct": -0.5},
    }
    for symbol, m in metrics.items():
        db.save_stock_metrics(symbol, m)
    db.flush()

    # 5 years of annual earnings for growth/consistency/Buffett metrics
    earnings = {
        "AAPL": [
            (2019, 2.97, 260e9, 55.3e9, 69.4e9, -10.5e9, 90488e6),
            (2020, 3.28, 275e9, 57.4e9, 80.7e9, -7.3e9, 65339e6),
            (2021, 5.61, 366e9, 94.7e9, 104.0e9, -11.1e9, 63090e6),
            (2022, 6.11, 394e9, 99.8e9, 122.2e9, -10.7e9, 50672e6),
            (2023, 6.13, 383e9, 97.0e9, 110.5e9, -10.9e9, 62146e6),
        ],
        "MSFT": [
            (2019, 5.06, 125.8e9, 39.2e9, 52.2e9, -15.4e9, 102330e6),
            (2020, 5.76, 143.0e9, 44.3e9, 60.7e9, -15.4e9, 118304e6),
            (2021, 8.05, 168.1e9, 61.3e9, 76.7e9, -20.6e9, 141988e6),
            (2022, 9.21, 198.3e9, 72.7e9, 89.0e9, -23.9e9, 166542e6),
            (2023, 9.68, 212.0e9, 72.4e9, 87.6e9, -28.1e9, 206223e6),
        ],
        "JNJ": [
            (2019, 5.63, 82.1e9, 15.1e9, 23.4e9, -3.5e9, 59471e6),
            (2020, 5.51, 82.6e9, 14.7e9, 23.5e9, -4.0e9, 63278e6),
            (2021, 7.81, 93.8e9, 20.9e9, 23.4e9, -4.5e9, 74023e6),
            (2022, 6.73, 94.9e9, 17.9e9, 21.2e9, -4.3e9, 76804e6),
            (2023, 7.33, 85.2e9, 35.2e9, 20.2e9, -4.0e9, 68774e6),
        ],
    }
    for symbol, years in earnings.items():
        for year, eps, rev, ni, ocf, capex, equity in years:
            db.save_earnings_history(
                symbol, year, eps, rev,
                net_income=ni,
                operating_cash_flow=ocf,
                capital_expenditures=capex,
                shareholder_equity=equity,
            )
    db.flush()


class TestVectorizedScoring:
    """Test suite for vectorized scoring parity."""

    @pytest.fixture
    def setup(self, db):
        """Set up services and seed test data."""
        _seed_stock_data(db)
        analyzer = EarningsAnalyzer(db)
        criteria = LynchCriteria(db, analyzer)
        vectors = StockVectors(db)
        return db, analyzer, criteria, vectors
    
    def test_load_vectors(self, setup):
        """Test that vectors load successfully with expected columns."""
        db, analyzer, criteria, vectors = setup
        
        df = vectors.load_vectors(country_filter='US')
        
        # Check required columns exist
        required_columns = [
            'symbol', 'price', 'market_cap', 'pe_ratio', 'debt_to_equity',
            'institutional_ownership', 'sector', 'company_name',
            'earnings_cagr', 'revenue_cagr', 'peg_ratio',
            'income_consistency_score', 'revenue_consistency_score'
        ]
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"
        
        # Should have some stocks
        assert len(df) > 0, "No stocks loaded"
        print(f"Loaded {len(df)} stocks")
    
    def test_evaluate_batch_output_shape(self, setup):
        """Test that evaluate_batch returns expected columns."""
        db, analyzer, criteria, vectors = setup
        
        df = vectors.load_vectors(country_filter='US')
        result = criteria.evaluate_batch(df, DEFAULT_ALGORITHM_CONFIG)
        
        # Check output columns
        required_columns = [
            'symbol', 'overall_score', 'overall_status',
            'peg_score', 'peg_status',
            'debt_score', 'debt_status',
            'institutional_ownership_score', 'institutional_ownership_status'
        ]
        for col in required_columns:
            assert col in result.columns, f"Missing output column: {col}"
        
        # Should have same number of rows as input
        assert len(result) == len(df)
        
        # Should be sorted by overall_score descending
        scores = result['overall_score'].tolist()
        assert scores == sorted(scores, reverse=True), "Results not sorted by score"
    
    def test_score_parity_sample(self, setup):
        """Test that vectorized scores match scalar scores for sample stocks."""
        db, analyzer, criteria, vectors = setup
        
        # Load vectors
        df = vectors.load_vectors(country_filter='US')
        
        # Align configuration with what LynchCriteria loaded from DB
        # This is critical because the test DB might have optimized/seeded settings 
        # that differ from the hardcoded DEFAULT_ALGORITHM_CONFIG
        config = DEFAULT_ALGORITHM_CONFIG.copy()
        if hasattr(criteria, 'settings'):
            for key, data in criteria.settings.items():
                if isinstance(data, dict) and 'value' in data:
                    config[key] = data['value']
        
        batch_result = criteria.evaluate_batch(df, config)
        
        # Sample 10 stocks (or fewer if less available)
        sample_size = min(10, len(batch_result))
        sample_symbols = batch_result['symbol'].head(sample_size).tolist()
        
        mismatches = []
        
        for symbol in sample_symbols:
            # Get batch score
            batch_row = batch_result[batch_result['symbol'] == symbol].iloc[0]
            batch_score = batch_row['overall_score']
            batch_status = batch_row['overall_status']
            
            # Get scalar score
            scalar_result = criteria.evaluate_stock(symbol, algorithm='weighted')
            if scalar_result is None:
                continue
            
            scalar_score = scalar_result.get('overall_score', 0)
            scalar_status = scalar_result.get('overall_status', '')
            
            # Allow small floating point difference
            if abs(batch_score - scalar_score) > 0.1:
                mismatches.append({
                    'symbol': symbol,
                    'batch_score': batch_score,
                    'scalar_score': scalar_score,
                    'diff': abs(batch_score - scalar_score)
                })
            
            if batch_status != scalar_status:
                 mismatches.append({
                    'symbol': symbol,
                    'batch_status': batch_status,
                    'scalar_status': scalar_status
                })
        
        if mismatches:
            print("Score mismatches found:")
            for m in mismatches:
                print(f"  {m}")
                
        assert len(mismatches) == 0, f"Found {len(mismatches)} score mismatches"
    
    def test_performance(self, setup):
        """Test that vectorized scoring completes quickly."""
        import time
        
        db, analyzer, criteria, vectors = setup
        
        start = time.time()
        df = vectors.load_vectors(country_filter='US')
        load_time = time.time() - start
        
        start = time.time()
        result = criteria.evaluate_batch(df, DEFAULT_ALGORITHM_CONFIG)
        score_time = time.time() - start
        
        total_time = load_time + score_time
        
        print(f"Load time: {load_time*1000:.0f}ms")
        print(f"Score time: {score_time*1000:.0f}ms")
        print(f"Total time: {total_time*1000:.0f}ms")
        print(f"Stocks processed: {len(result)}")
        
        # Should complete in under 5.0s (User goal requirement)
        assert total_time < 5.0, f"Vectorized scoring too slow: {total_time*1000:.0f}ms"

    def test_buffett_scoring(self, setup):
        """Test Buffett scoring logic."""
        db, analyzer, criteria, vectors = setup
        
        # Load vectors
        df = vectors.load_vectors(country_filter='US')
        
        # Buffett Config
        buffett_config = {
            'weight_roe': 0.40,
            'weight_consistency': 0.30,
            'weight_debt_to_earnings': 0.30,
            'roe_excellent': 20.0,
            'roe_good': 15.0,
            'roe_fair': 10.0,
            'debt_to_earnings_excellent': 2.0,
            'debt_to_earnings_good': 4.0,
            'debt_to_earnings_fair': 7.0,
        }
        
        result = criteria.evaluate_batch(df, buffett_config)
        
        # Check output columns
        expected_cols = ['roe', 'debt_to_earnings', 'roe_score', 'debt_to_earnings_score']
        for col in expected_cols:
            if col not in result.columns:
                print(f"Warning: {col} missing (might be empty/None if no data)")
        
        # Verify scores are populated (at least some)
        if len(result) > 0:
            assert 'overall_score' in result.columns
            print(f"Top Buffett Stock: {result.iloc[0]['symbol']} Score: {result.iloc[0]['overall_score']}")

    def test_buffett_performance(self, setup):
        """Test that Buffett vectorized scoring is fast."""
        import time
        db, analyzer, criteria, vectors = setup
        
        buffett_config = {
            'weight_roe': 0.40,
            'weight_consistency': 0.30,
            'weight_debt_to_earnings': 0.30,
        }
        
        start = time.time()
        df = vectors.load_vectors(country_filter='US')
        load_time = time.time() - start
        
        start = time.time()
        result = criteria.evaluate_batch(df, buffett_config)
        score_time = time.time() - start
        
        total_time = load_time + score_time
        print(f"Buffett Total Time: {total_time*1000:.0f}ms")
        
        assert total_time < 5.0, f"Buffett scoring too slow: {total_time*1000:.0f}ms"


if __name__ == '__main__':
    # Run with: python test_vectorized_scoring.py
    pytest.main([__file__, '-v', '-s'])
