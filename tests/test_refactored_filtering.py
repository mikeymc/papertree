import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import Database
from strategy_executor.universe_filter import UniverseFilter
from scoring.vectors import StockVectors

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_refactored_filtering():
    db = Database()
    uf = UniverseFilter(db)
    vectors = StockVectors(db)
    
    print("1. Testing Single Country Filter (US)...")
    conditions_us = {
        'filters': [
            {'field': 'country', 'value': 'US', 'operator': '=='},
            {'field': 'market_cap', 'value': 1000000000, 'operator': '>='} # > 1B
        ]
    }
    
    symbols_us = uf.filter_universe(conditions_us)
    print(f"   Found {len(symbols_us)} US symbols > $1B")
    
    print("\n2. Testing Multi-Country Filter (US, CA)...")
    # Exact structure from peter_lynch_classic
    conditions_multi = {
        'filters': [
            {'field': 'country', 'value': ['US', 'CA', 'GB', 'DE'], 'operator': 'in'},
             {'field': 'market_cap', 'value': 100000000, 'operator': '>='}
        ]
    }
    
    symbols_multi = uf.filter_universe(conditions_multi)
    print(f"   Found {len(symbols_multi)} US+CA+GB+DE symbols > $100M")
    
    print("\n3. Testing Region Filter (North America)...")
    # Exact structure from lynch_buffett_pair
    conditions_region = {
        'filters': [
            {'field': 'region', 'value': 'North America', 'operator': '=='}, # US, CA, MX
            {'field': 'market_cap', 'value': 1000000000, 'operator': '>='}
        ]
    }
    symbols_region = uf.filter_universe(conditions_region)
    print(f"   Found {len(symbols_region)} North America symbols > $1B")

    print("\n4. Testing Scoring Integrity (Qualitative checks)...")
    # We want to ensure we didn't filter out high PEG stocks, but that they just get low scores later.
    # This verification is harder without running full scoring, but we can check if `universe_filter` 
    # returns stocks that WOULD have been filtered by PEG > 1.5.
    
    # Let's find a stock with PEG > 2.0 in the `vectors` dataframe for US
    df = vectors.load_vectors(country_filter='US')
    high_peg_stocks = df[df['peg_ratio'] > 2.0]['symbol'].tolist()
    
    if high_peg_stocks:
        print(f"   Found {len(high_peg_stocks)} US stocks with PEG > 2.0 (e.g., {high_peg_stocks[:3]})")
        # Ensure these are in the filtered list (since we removed PEG filter from templates)
        # Using pure universe filter (market cap > 100M)
        
        conditions_univ = {
            'filters': [
                {'field': 'country', 'value': 'US', 'operator': '=='},
                {'field': 'market_cap', 'value': 100000000, 'operator': '>='} 
            ]
        }
        filtered = uf.filter_universe(conditions_univ)
        
        # Check intersection
        kept_high_peg = set(high_peg_stocks).intersection(set(filtered))
        print(f"   Of those, {len(kept_high_peg)} are kept by Universe Filter (Correct behavior)")
        
        if len(kept_high_peg) == 0:
            print("   WARNING: High PEG stocks were filtered out! Check if default filters are applied?")
        else:
            print("   SUCCESS: High PEG stocks are retained for scoring.")
            
    else:
        print("   No high PEG stocks found in DB? (Data might be sparse)")

if __name__ == "__main__":
    test_refactored_filtering()
