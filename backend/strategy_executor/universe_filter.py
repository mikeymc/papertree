# ABOUTME: Parses and evaluates strategy conditions against stock data
# ABOUTME: Applies universe filters to return candidate symbols using vectorized data

import logging
import pandas as pd
from typing import Dict, Any, List
from scoring.vectors import StockVectors

logger = logging.getLogger(__name__)


class UniverseFilter:
    """Parses and evaluates strategy conditions against stock data."""

    def __init__(self, db):
        self.db = db
        self.stock_vectors = StockVectors(db)

    def filter_universe(self, conditions: Dict[str, Any]) -> List[str]:
        """Apply universe filters to return candidate symbols.

        Args:
            conditions: Strategy conditions with 'filters' key containing filters

        Returns:
            List of symbols that match all filters
        """
        filters = conditions.get('filters', [])

        # Load all stock data via vectorized engine (handles growth/Buffett metrics)
        # Use US filter by default as per production settings
        df = self.stock_vectors.load_vectors(country_filter='US')

        if not filters:
            # No filters = return all symbols in the universe
            return df['symbol'].tolist()

        # Apply each filter sequentially to the DataFrame
        for filter_spec in filters:
            df = self._apply_filter(df, filter_spec)

        return df['symbol'].tolist()

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
            'revenue_growth': 'revenue_cagr'
        }

        col = field_mapping.get(field, field)

        if col not in df.columns:
            logger.warning(f"[UniverseFilter] Unsupported filter field: {field} (mapped to {col})")
            return df

        try:
            # Convert value to float for numeric comparison if possible
            if isinstance(value, (str, int)):
                try:
                    value = float(value)
                except ValueError:
                    pass

            # Normalize institutional_ownership (UI sends percentage 0-100, DB stores decimal 0-1)
            if col == 'institutional_ownership':
                # If the value is > 2, it's definitely a percentage. 
                # If it's 0-2, it could be either, but we'll assume percentage based on UI labels.
                # Note: Some stocks have > 100% inst ownership due to shorts/reporting lags, so we use a high threshold.
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
                mask = df[col] == value
            elif operator == '!=':
                mask = df[col] != value
            else:
                logger.warning(f"[UniverseFilter] Unsupported operator: {operator}")
                return df

            # Apply mask to DataFrame
            return df[mask]
        except Exception as e:
            logger.error(f"[UniverseFilter] Error applying filter {field} {operator} {value}: {e}")
            return df
