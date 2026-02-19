# ABOUTME: Scoring mixin for candidate evaluation with Lynch/Buffett criteria
# ABOUTME: Handles Phase 2 of strategy execution with vectorized batch scoring

import logging
from typing import Dict, Any, List

from strategy_executor.utils import log_event

logger = logging.getLogger(__name__)


class ScoringMixin:
    """Phase 2: Candidate scoring with Lynch/Buffett criteria."""

    def _score_candidates(
        self,
        candidates: List[str],
        conditions: Dict[str, Any],
        run_id: int,
        is_addition: bool = False,
        analysts: List[str] = None
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Score candidates with Lynch and Buffett scoring.

        Args:
            candidates: List of symbols to score
            conditions: Strategy conditions with scoring requirements
            run_id: Current run ID for logging
            is_addition: If True, use higher thresholds for position additions

        Returns:
            Tuple of (passing, declined). For is_addition=True, declined contains
            held stocks that have score data but failed addition thresholds — they
            are routed through deliberation for exit evaluation. For is_addition=False,
            declined is always empty.
        """
        if not candidates:
            return [], []

        if analysts is None:
            analysts = ['lynch', 'buffett']

        # 1. Determine thresholds
        # This now returns a dict {analyst: threshold}
        scoring_thresholds = self._get_scoring_thresholds(conditions, is_addition, analysts)

        position_type = "addition" if is_addition else "new position"
        
        analyst_str = ", ".join(analysts)
        threshold_str = ", ".join([f"{a.capitalize()}: {scoring_thresholds.get(a)}" for a in analysts])
        log_event(self.db, run_id, f"Scoring {len(candidates)} {position_type} candidates with {analyst_str} ({threshold_str})")

        try:
            # 2. Load Data
            df = self._load_candidate_data(candidates, run_id)
            if df is None or df.empty:
                return [], []

            # 3. Calculate Scores
            df_scores = self._calculate_batch_scores(df, analysts)

            # 4. Evaluate Candidates
            scored, declined = self._evaluate_candidates(df_scores, scoring_thresholds, is_addition, run_id, analysts)

            log_event(self.db, run_id, f"Scoring complete: {len(scored)}/{len(candidates)} {position_type}s passed requirements")
            return scored, declined

        except Exception as e:
            logger.error(f"Vectorized scoring failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            log_event(self.db, run_id, f"ERROR: Vectorized scoring failed: {e}")
            return [], []

    def _get_scoring_thresholds(self, conditions: Dict[str, Any], is_addition: bool, analysts: List[str]) -> Dict[str, int]:
        """Determine score thresholds for active analysts."""
        from scoring.core import SCORE_THRESHOLDS

        scoring_reqs = conditions.get('scoring_requirements', [])
        default_min = SCORE_THRESHOLDS.get('BUY', 60)
        
        thresholds = {a: default_min for a in analysts}

        if is_addition:
            addition_reqs = conditions.get('addition_scoring_requirements', [])
            if addition_reqs:
                for req in addition_reqs:
                    char = req.get('character')
                    if char in thresholds:
                         thresholds[char] = int(req.get('min_score', default_min))
            else:
                # Default: +10 higher than base requirements
                # First get base reqs
                base_thresholds = {a: default_min for a in analysts}
                for req in scoring_reqs:
                    char = req.get('character')
                    if char in base_thresholds:
                         base_thresholds[char] = int(req.get('min_score', default_min))
                
                # Apply +10
                for a in analysts:
                    thresholds[a] = base_thresholds[a] + 10
        else:
            for req in scoring_reqs:
                char = req.get('character')
                if char in thresholds:
                    thresholds[char] = int(req.get('min_score', default_min))

        return thresholds

    def _load_candidate_data(self, candidates: List[str], run_id: int):
        """Load vectorized stock data for candidates."""
        import pandas as pd
        from scoring.vectors import StockVectors

        print(f"  Loading stock data for {len(candidates)} candidates...")

        vectors = StockVectors(self.db)
        df_all = vectors.load_vectors()

        if df_all is None or df_all.empty:
            log_event(self.db, run_id, "No stock data available for scoring")
            return None

        # Filter to just our candidates
        df = df_all[df_all['symbol'].isin(candidates)].copy()

        if df.empty:
            log_event(self.db, run_id, f"No data found for candidates: {candidates[:5]}...")
            return None

        print(f"  Found data for {len(df)} stocks")
        return df

    def _calculate_batch_scores(self, df, analysts: List[str]):
        """Calculate scores for the dataframe for specified analysts."""
        from scoring.vectors import DEFAULT_ALGORITHM_CONFIG
        from characters.buffett import BUFFETT
        import pandas as pd

        dfs_to_merge = []
        
        # Always start with symbol column
        df_base = df[['symbol']].copy()
        dfs_to_merge.append(df_base)

        if 'lynch' in analysts:
            # Score with Lynch
            print(f"  Scoring with Lynch criteria...")
            df_lynch = self.lynch_criteria.evaluate_batch(df, DEFAULT_ALGORITHM_CONFIG)
            df_lynch_scores = df_lynch[['symbol', 'overall_score', 'overall_status']].rename(
                columns={'overall_score': 'lynch_score', 'overall_status': 'lynch_status'}
            )
            dfs_to_merge.append(df_lynch_scores)

        if 'buffett' in analysts:
            # Score with Buffett
            print(f"  Scoring with Buffett criteria...")
            buffett_config = {}
            for sw in BUFFETT.scoring_weights:
                if sw.metric == 'roe':
                    buffett_config['weight_roe'] = sw.weight
                    buffett_config['roe_excellent'] = sw.threshold.excellent
                    buffett_config['roe_good'] = sw.threshold.good
                    buffett_config['roe_fair'] = sw.threshold.fair
                elif sw.metric == 'debt_to_earnings':
                    buffett_config['weight_debt_to_earnings'] = sw.weight
                    buffett_config['debt_to_earnings_excellent'] = sw.threshold.excellent
                    buffett_config['debt_to_earnings_good'] = sw.threshold.good
                    buffett_config['debt_to_earnings_fair'] = sw.threshold.fair
                elif sw.metric == 'gross_margin':
                    buffett_config['weight_gross_margin'] = sw.weight
                    buffett_config['gross_margin_excellent'] = sw.threshold.excellent
                    buffett_config['gross_margin_good'] = sw.threshold.good
                    buffett_config['gross_margin_fair'] = sw.threshold.fair
                elif sw.metric == 'earnings_consistency':
                    buffett_config['weight_consistency'] = sw.weight
                    buffett_config['consistency_null_default'] = 0.0  # Buffett is harsher on missing data

            df_buffett = self.lynch_criteria.evaluate_batch(df, buffett_config)
            df_buffett_scores = df_buffett[['symbol', 'overall_score', 'overall_status']].rename(
                columns={'overall_score': 'buffett_score', 'overall_status': 'buffett_status'}
            )
            dfs_to_merge.append(df_buffett_scores)

        # Merge all score dataframes
        df_merged = dfs_to_merge[0]
        for i in range(1, len(dfs_to_merge)):
            df_merged = df_merged.merge(dfs_to_merge[i], on='symbol', how='inner')
            
        return df_merged

    def _evaluate_candidates(self, df_scores, scoring_thresholds, is_addition, run_id, analysts):
        """Evaluate scored candidates against requirements."""
        scored = []
        declined = []
        df_scores['position_type'] = 'addition' if is_addition else 'new'
        type_label = "ADDITION" if is_addition else "NEW"

        for _, row in df_scores.iterrows():
            symbol = row['symbol']
            stock_data = {
                'symbol': symbol,
                'position_type': row['position_type']
            }
            
            # Populate scores
            log_parts = []
            if 'lynch' in analysts:
                stock_data['lynch_score'] = row['lynch_score']
                stock_data['lynch_status'] = row['lynch_status']
                log_parts.append(f"Lynch {row['lynch_score']:.0f}")
            else:
                 stock_data['lynch_score'] = 0 # Default/Null
                 stock_data['lynch_status'] = 'N/A'

            if 'buffett' in analysts:
                stock_data['buffett_score'] = row['buffett_score']
                stock_data['buffett_status'] = row['buffett_status']
                log_parts.append(f"Buffett {row['buffett_score']:.0f}")
            else:
                 stock_data['buffett_score'] = 0
                 stock_data['buffett_status'] = 'N/A'

            score_str = ", ".join(log_parts)
            print(f"  {symbol} ({type_label}): {score_str}")

            # Check if passes scoring requirements (OR Logic)
            passes = False
            pass_reasons = []
            fail_reasons = []

            for analyst in analysts:
                score_key = f"{analyst}_score"
                score = row.get(score_key, 0)
                threshold = scoring_thresholds.get(analyst, 60)
                
                if score >= threshold:
                    passes = True
                    pass_reasons.append(f"{analyst.capitalize()} {score:.0f} >= {threshold}")
                else:
                    fail_reasons.append(f"{analyst.capitalize()} {score:.0f} < {threshold}")

            if passes:
                scored.append(stock_data)
                reason_str = ", ".join(pass_reasons)
                threshold_note = " (higher bar for additions)" if is_addition else ""

                print(f"    ✓ PASSED requirements ({reason_str}){threshold_note}")
                logger.debug(f"{symbol}: PASSED as {type_label} ({reason_str})")
            else:
                fail_str = ", ".join(fail_reasons)
                threshold_note = " (higher bar for additions)" if is_addition else ""
                print(f"    ✗ FAILED requirements ({fail_str}){threshold_note}")

                if is_addition:
                    stock_data['position_type'] = 'held_exit_evaluation'
                    declined.append(stock_data)

        return scored, declined
