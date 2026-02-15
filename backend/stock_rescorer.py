# ABOUTME: Re-scores stocks from latest screening session using the vector scoring path
# ABOUTME: Handles batch processing and database updates for screening_results table

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from stock_vectors import StockVectors, DEFAULT_ALGORITHM_CONFIG

logger = logging.getLogger(__name__)


class StockRescorer:
    def __init__(self, db, criteria):
        self.db = db
        self.criteria = criteria

    def rescore_saved_stocks(self, algorithm: str = 'weighted', progress_callback=None) -> Dict[str, Any]:
        """
        Re-score all stocks from the latest screening session.

        Args:
            algorithm: Unused — kept for API compatibility; vector path always uses
                       DEFAULT_ALGORITHM_CONFIG (weighted Lynch scoring).
            progress_callback: Optional callback function(current, total) to report progress

        Returns:
            Summary dict with counts and any errors
        """
        logger.info("Starting re-scoring of stocks from latest screening session...")

        latest_session = self.db.get_latest_session()
        if not latest_session:
            logger.info("No screening sessions found")
            return {'total': 0, 'success': 0, 'failed': 0, 'errors': []}

        session_id = latest_session['session_id']
        symbols_to_rescore = self.db.get_screening_symbols(session_id)

        if not symbols_to_rescore:
            logger.info("No stocks in latest screening session")
            return {'total': 0, 'success': 0, 'failed': 0, 'errors': []}

        total = len(symbols_to_rescore)
        logger.info(f"Re-scoring {total} stocks from session {session_id}...")

        # Load vector universe and filter to session symbols
        vectors = StockVectors(self.db)
        df_all = vectors.load_vectors()
        df = df_all[df_all['symbol'].isin(symbols_to_rescore)].copy()

        results = []
        errors = []

        if not df.empty:
            scored_df = self.criteria.evaluate_batch(df, DEFAULT_ALGORITHM_CONFIG)
            scored_map = {row['symbol']: row for _, row in scored_df.iterrows()}

            for symbol in symbols_to_rescore:
                if symbol in scored_map:
                    row = scored_map[symbol]
                    results.append({
                        'symbol': symbol,
                        'success': True,
                        'evaluation': {
                            'overall_score': row['overall_score'],
                            'overall_status': row['overall_status'],
                            'peg_score': row.get('peg_score'),
                            'debt_score': row.get('debt_score'),
                            'institutional_ownership_score': row.get('institutional_ownership_score'),
                        },
                        'scored_at': datetime.now(),
                    })
                else:
                    errors.append(f"{symbol}: not in vector universe")
                    results.append({'symbol': symbol, 'success': False, 'error': 'Not in vector universe'})
        else:
            for symbol in symbols_to_rescore:
                errors.append(f"{symbol}: no vector data available")
                results.append({'symbol': symbol, 'success': False, 'error': 'No vector data available'})

        if progress_callback:
            progress_callback(total, total)

        self._update_database(results)

        success_count = sum(1 for r in results if r['success'])
        logger.info(f"✓ Re-scoring complete: {success_count}/{total} successful")
        return {
            'total': total,
            'success': success_count,
            'failed': total - success_count,
            'errors': errors,
        }

    def _update_database(self, results: List[Dict[str, Any]]):
        """Update screening_results table with new scores."""
        for result in results:
            if not result['success']:
                continue
            symbol = result['symbol']
            evaluation = result['evaluation']
            scored_at = result['scored_at']
            self.db.update_screening_result_scores(
                symbol=symbol,
                overall_score=evaluation.get('overall_score'),
                overall_status=evaluation.get('overall_status'),
                peg_score=evaluation.get('peg_score'),
                debt_score=evaluation.get('debt_score'),
                institutional_ownership_score=evaluation.get('institutional_ownership_score'),
                scored_at=scored_at,
            )
