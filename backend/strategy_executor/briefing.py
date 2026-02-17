# ABOUTME: Generates post-run briefings combining structured data with AI narrative
# ABOUTME: Assembles trade/hold/watch data from decisions and calls Gemini for executive summary

import json
import logging
import os
from typing import Dict, Any

from google import genai

logger = logging.getLogger(__name__)


class BriefingGenerator:

    def __init__(self, db):
        self.db = db

    def generate(
        self,
        run_id: int,
        strategy_id: int,
        portfolio_id: int,
        performance: Dict[str, Any],
    ) -> Dict[str, Any]:
        logger.info(f"[Briefing] Starting generation for run {run_id}...")
        
        # 1. Fetch relevant data
        """Generate a briefing for a completed strategy run.

        Pulls decisions from the DB, categorizes them, and generates an AI summary.
        Returns a dict ready for db.save_briefing().
        """
        run = self.db.get_strategy_run(run_id)
        decisions = self.db.get_run_decisions(run_id)

        # Categorize decisions
        buys = []
        sells = []
        holds = []
        watchlist = []

        for d in decisions:
            decision = d.get('final_decision')
            
            # Truncation logic: 
            # - Buys/Sells get full deliberation (capped)
            # - Holds/Watchlist get summary only
            is_critical = decision in ['BUY', 'SELL']
            deliberative_text = ""
            
            if is_critical:
                # Keep full deliberation but cap at 10k chars as safety
                deliberative_text = (d.get('thesis_full') or d.get('thesis_summary') or "")[:10000]
            else:
                # For non-critical, prefer summary, fallback to first 500 chars of full
                deliberative_text = d.get('thesis_summary')
                if not deliberative_text and d.get('thesis_full'):
                    deliberative_text = d.get('thesis_full')[:500] + "..."
            
            entry = {
                'symbol': d['symbol'],
                'reasoning': d.get('decision_reasoning', ''),
                'lynch_score': d.get('lynch_score'),
                'buffett_score': d.get('buffett_score'),
                'lynch_status': d.get('lynch_status'),
                'buffett_status': d.get('buffett_status'),
                'consensus_verdict': d.get('consensus_verdict'),
                'consensus_score': d.get('consensus_score'),
                'dcf_fair_value': d.get('dcf_fair_value'),
                'dcf_upside_pct': d.get('dcf_upside_pct'),
                'deliberation': deliberative_text or "",
            }

            if decision == 'BUY':
                # Filter: Only include if actually traded or queued
                # Fix: Handle None for shares_traded safely
                shares = d.get('shares_traded')
                if shares is None:
                    shares = 0
                
                if (d.get('transaction_id') or 
                    (shares > 0) or 
                    'QUEUED' in str(d.get('decision_reasoning', '')) or
                    'PENDING' in str(d.get('decision_reasoning', ''))):
                    
                    entry['shares'] = shares
                    entry['price'] = d.get('trade_price')
                    entry['position_value'] = d.get('position_value')
                    buys.append(entry)
                else:
                    # Treat as skipped/watchlist if not executed
                    entry['verdict'] = 'WATCH (Skipped)'
                    watchlist.append(entry)

            elif decision == 'SELL':
                shares = d.get('shares_traded') or 0
                if (d.get('transaction_id') or 
                    (shares > 0) or 
                    'QUEUED' in str(d.get('decision_reasoning', ''))):
                    
                    entry['shares'] = shares
                    entry['price'] = d.get('trade_price')
                    entry['position_value'] = d.get('position_value')
                    entry['exit_type'] = 'strategy'
                    sells.append(entry)
                else:
                    # Failed sell -> Hold
                    entry['verdict'] = 'HOLD (Failed Sell)'
                    holds.append(entry)
            elif decision == 'HOLD':
                entry['verdict'] = d.get('thesis_verdict', 'HOLD')
                entry['position_value'] = d.get('position_value')
                holds.append(entry)
            elif decision == 'SKIP':
                entry['verdict'] = d.get('thesis_verdict', 'WATCH')
                watchlist.append(entry)

        # Filter non-critical lists to prevent token exhaustion
        # Note: We sort watchlist by consensus score (desc) to keep the best "near misses"
        watchlist.sort(key=lambda x: x.get('consensus_score') or 0, reverse=True)
        watchlist = watchlist[:20]
        
        # Holds: Just take the top 50 (no specific sort, usually by portfolio weight is fine but we don't have it here easily)
        holds = holds[:50]

        logger.info(f"[Briefing] Run {run_id} breakdown: {len(buys)} Buys, {len(sells)} Sells, {len(holds)} Holds (sampled), {len(watchlist)} Watchlist (top 20)")

        # Build structured data
        briefing = {
            'run_id': run_id,
            'strategy_id': strategy_id,
            'portfolio_id': portfolio_id,
            'stocks_screened': run.get('stocks_screened', 0),
            'stocks_scored': run.get('stocks_scored', 0),
            'theses_generated': run.get('theses_generated', 0),
            'trades_executed': run.get('trades_executed', 0),
            'portfolio_value': performance.get('portfolio_value'),
            'portfolio_return_pct': performance.get('portfolio_return_pct'),
            'spy_return_pct': performance.get('spy_return_pct'),
            'alpha': performance.get('alpha'),
            'buys_json': json.dumps(buys),
            'sells_json': json.dumps(sells),
            'holds_json': json.dumps(holds),
            'watchlist_json': json.dumps(watchlist),
        }

        # Collect all symbols to provide a name mapping for the AI
        all_symbols = set()
        for s in buys + sells + holds + watchlist:
            if s.get('symbol'):
                all_symbols.add(s['symbol'])
        
        # Get names from DB if possible
        stock_ref_map = {}
        if all_symbols:
            try:
                # We can use search_stocks or similar, but simpler to just use get_stock_metrics or raw SQL
                # Actually BriefingGenerator has self.db which is expected to have these methods.
                # Let's try to get them in a batch if the DB supports it, or individual lookups as a fallback.
                for symbol in all_symbols:
                    m = self.db.get_stock_metrics(symbol)
                    if m and m.get('company_name'):
                        stock_ref_map[symbol] = m['company_name']
                    else:
                        stock_ref_map[symbol] = symbol
            except Exception as e:
                logger.warning(f"Failed to fetch stock names for briefing: {e}")

        # Format stock reference for prompt
        stock_ref_str = "\n".join([f"- {sym}: {name}" for sym, name in stock_ref_map.items()])
        briefing['stock_reference'] = stock_ref_str

        # Generate AI executive summary
        briefing['executive_summary'] = self._generate_executive_summary(briefing)

        logger.info(f"[Briefing] Successfully generated briefing for run {run_id}")
        return briefing

    def _generate_executive_summary(self, briefing: Dict[str, Any]) -> str:
        """Generate a detailed AI briefing covering trades, rationale, and portfolio posture."""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_path = os.path.join(current_dir, 'briefing_prompt.md')

            with open(prompt_path, 'r') as f:
                prompt_template = f.read()

            prompt = prompt_template.format(
                stocks_screened=briefing.get('stocks_screened', 0),
                stocks_scored=briefing.get('stocks_scored', 0),
                theses_generated=briefing.get('theses_generated', 0),
                trades_executed=briefing.get('trades_executed', 0),
                portfolio_value=briefing.get('portfolio_value', 0),
                portfolio_return_pct=briefing.get('portfolio_return_pct', 0),
                spy_return_pct=briefing.get('spy_return_pct', 0),
                alpha=briefing.get('alpha', 0),
                buys=briefing.get('buys_json', '[]'),
                sells=briefing.get('sells_json', '[]'),
                holds=briefing.get('holds_json', '[]'),
                watchlist=briefing.get('watchlist_json', '[]'),
                stock_reference=briefing.get('stock_reference', ''),
            )

            from google.genai.types import GenerateContentConfig
            client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
            response = client.models.generate_content(
                model='gemini-3-flash-preview',
                contents=prompt,
                config=GenerateContentConfig(temperature=0.7),
            )
            return response.text

        except Exception as e:
            logger.warning(f"Failed to generate executive summary: {e}")
            return f"Strategy run completed. Unable to generate AI summary: {e}"
