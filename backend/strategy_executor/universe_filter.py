# ABOUTME: Parses and evaluates strategy conditions against stock data
# ABOUTME: Applies universe filters to return candidate symbols using vectorized data

import logging
import pandas as pd
from typing import Dict, Any, List
from scoring.vectors import StockVectors

logger = logging.getLogger(__name__)


class UniverseFilter:
    """Parses and evaluates strategy conditions against stock data."""


    def __init__(self, db, stock_vectors=None):
        self.db = db
        self.stock_vectors = stock_vectors or StockVectors(db)

    def filter_universe(self, conditions: Dict[str, Any]) -> List[str]:
        """Apply universe filters to return candidate symbols.

        Args:
            conditions: Strategy conditions with 'filters' key containing filters

        Returns:
            List of symbols that match all filters
        """
        filters = conditions.get('filters', [])
        
        # Extract country/region filters to optimize vector loading
        country_filter = ['US'] # Default for backward compatibility if nothing specified
        explicit_country_filter = False
        
        # Check for explicit country or region filters
        for f in filters:
            if f.get('field') == 'country':
                val = f.get('value')
                # Handle list or comma-separated string
                if isinstance(val, str) and ',' in val:
                    country_filter = [x.strip() for x in val.split(',')]
                elif isinstance(val, list):
                    country_filter = val
                else:
                    country_filter = [val]
                explicit_country_filter = True
            elif f.get('field') == 'region':
                val = f.get('value')
                # Expand region to countries
                countries = self._expand_region_to_countries(val)
                if countries:
                    country_filter = countries
                    explicit_country_filter = True

        # Load all stock data via vectorized engine (handles growth/Buffett metrics)
        # If no explicit filter found, we default to US (as per previous logic)
        # unless user passed 'Global' or empty list? 
        # For now, keeping default='US' logic effectively.
        
        # If explicitly requested 'Global' or similar, we might want to pass None?
        # Assuming UI passes specific countries or regions.
        
        df = self.stock_vectors.load_vectors(country_filter=country_filter)

        if not filters:
            # No filters = return all symbols in the universe (loaded based on country)
            return df['symbol'].tolist()

        # Apply each filter sequentially to the DataFrame
        for filter_spec in filters:
            # Skip country/region filters as they are handled at load time
            # (unless we want to double check, but load_vectors does strictly filter)
            if filter_spec.get('field') in ['country', 'region']:
                continue
                
            df = self._apply_filter(df, filter_spec)

        return df['symbol'].tolist()

    def _expand_region_to_countries(self, region: Any) -> List[str]:
        """Expand region name(s) to list of country codes."""
        regions = {
            'North America': ['US', 'CA'],
            'Europe': ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'CH', 'IE', 'BE', 'SE', 'NO', 'DK', 'FI', 'AT', 'PL', 'PT', 'GR', 'CZ', 'HU', 'RO', 'LU', 'IS'],
            'Asia': ['CN', 'JP', 'KR', 'IN', 'SG', 'HK', 'TW', 'TH', 'MY', 'ID', 'PH', 'VN', 'IL'],
            'Oceania': ['AU', 'NZ'],
            'South America': ['MX', 'BR', 'AR', 'CL', 'PE', 'CO', 'VE', 'EC', 'BO', 'PY', 'UY'],
        }
        
        target_regions = []
        if isinstance(region, list):
            target_regions = region
        else:
            target_regions = [region]
            
        countries = []
        for r in target_regions:
            if r in regions:
                countries.extend(regions[r])
        
        return list(set(countries)) # storage dedup

    def _apply_filter(self, df: pd.DataFrame, filter_spec: Dict[str, Any]) -> pd.DataFrame:
        """Apply a single filter to the DataFrame.

        Filter spec format:
        {
            "field": "roe",
            "operator": ">=",
            "value": 15
        }
        """
        field = filter_spec.get('field')
        operator = filter_spec.get('operator')
        value = filter_spec.get('value')

        if not all([field, operator, value is not None]) or df.empty:
            return df

        # Mapping of user-facing field names to StockVectors columns
        field_mapping = {
            'pe_ratio': 'pe_ratio',
            'market_cap': 'market_cap',
            'debt_to_equity': 'debt_to_equity',
            'dividend_yield': 'dividend_yield',
            'peg_ratio': 'peg_ratio',
            'price': 'price',
            'roe': 'roe',
            'debt_to_earnings': 'debt_to_earnings',
            'gross_margin': 'gross_margin',
            'institutional_ownership': 'institutional_ownership',
            'earnings_growth': 'earnings_cagr',
            'revenue_growth': 'revenue_cagr',
            'sector': 'sector',
            # country handled separately but mapped just in case
            'country': 'country'
        }

        col = field_mapping.get(field, field)

        if col not in df.columns:
            logger.warning(f"[UniverseFilter] Unsupported filter field: {field} (mapped to {col})")
            return df

        try:
            # Handle Numeric Conversions for non-list values
            if not isinstance(value, list) and isinstance(value, (str, int)) and col != 'sector':
                try:
                    value = float(value)
                except ValueError:
                    pass

            # Normalize institutional_ownership
            if col == 'institutional_ownership' and isinstance(value, (int, float)):
                 if value > 2:
                     value = value / 100.0

            # Apply operator
            if operator == '<':
                mask = df[col] < value
            elif operator == '>':
                mask = df[col] > value
            elif operator == '<=':
                mask = df[col] <= value
            elif operator == '>=':
                mask = df[col] >= value
            elif operator == '==':
                 if isinstance(value, list):
                     mask = df[col].isin(value)
                 else:
                     mask = df[col] == value
            elif operator == '!=':
                 if isinstance(value, list):
                     mask = ~df[col].isin(value)
                 else:
                     mask = df[col] != value
            elif operator == 'in': # Explicit support if specialized
                 if isinstance(value, list):
                     mask = df[col].isin(value)
                 else:
                     mask = df[col] == value # Fallback
            else:
                logger.warning(f"[UniverseFilter] Unsupported operator: {operator}")
                return df

            # Apply mask to DataFrame
            return df[mask]
        except Exception as e:
            logger.error(f"[UniverseFilter] Error applying filter {field} {operator} {value}: {e}")
            return df

