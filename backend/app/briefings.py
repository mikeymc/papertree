# ABOUTME: API endpoints for strategy run briefings
# ABOUTME: Serves briefings by portfolio and by individual briefing ID

from flask import Blueprint, jsonify, request
from app import deps
from auth import require_user_auth
import logging

logger = logging.getLogger(__name__)

briefings_bp = Blueprint('briefings', __name__)


@briefings_bp.route('/api/portfolios/<int:portfolio_id>/briefings', methods=['GET'])
@require_user_auth
def get_portfolio_briefings(user_id, portfolio_id):
    """Get all briefings for a portfolio."""
    limit = request.args.get('limit', 20, type=int)
    briefings = deps.db.get_briefings_for_portfolio(portfolio_id, limit=limit)

    # Convert datetime objects for JSON serialization
    result = []
    for b in briefings:
        item = dict(b)
        if item.get('generated_at'):
            item['generated_at'] = item['generated_at'].isoformat()

        # Enrich with analysts list from associated strategy
        strategy_id = item.get('strategy_id')
        if strategy_id:
            try:
                strategy = deps.db.get_strategy(strategy_id)
                if strategy:
                    conditions = strategy.get('conditions') or {}
                    if isinstance(conditions, str):
                        import json
                        conditions = json.loads(conditions)
                    item['analysts'] = conditions.get('analysts', ['lynch', 'buffett'])
            except Exception:
                item['analysts'] = ['lynch', 'buffett']
        else:
            item['analysts'] = ['lynch', 'buffett']

        # Build company_names map and character theses from symbols in trades data
        try:
            import json
            all_symbols = set()
            for json_field in ('buys_json', 'sells_json', 'holds_json'):
                entries = json.loads(item.get(json_field) or '[]')
                for e in entries:
                    if e.get('symbol'):
                        all_symbols.add(e['symbol'])
            company_names = {}
            character_theses = {}  # {symbol: {character_id: analysis_text}}
            for symbol in all_symbols:
                m = deps.db.get_stock_metrics(symbol)
                if m and m.get('company_name'):
                    company_names[symbol] = m['company_name']
                # Fetch individual character theses (shared cache, user 0)
                symbol_theses = {}
                for character_id in item.get('analysts', ['lynch', 'buffett']):
                    analysis = deps.db.get_lynch_analysis(0, symbol, character_id=character_id)
                    if analysis and analysis.get('analysis_text'):
                        symbol_theses[character_id] = analysis['analysis_text']
                if symbol_theses:
                    character_theses[symbol] = symbol_theses
            item['company_names'] = company_names
            item['character_theses'] = character_theses
        except Exception:
            item['company_names'] = {}
            item['character_theses'] = {}


        result.append(item)

    return jsonify(result)


@briefings_bp.route('/api/briefings/<int:briefing_id>', methods=['GET'])
@require_user_auth
def get_briefing(user_id, briefing_id):
    """Get a single briefing by ID."""
    conn = deps.db.get_connection()
    try:
        import psycopg.rows
        cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
        cursor.execute("""
            SELECT id, run_id, strategy_id, portfolio_id, candidates, qualifiers,
                   theses, targets, trades, portfolio_value, portfolio_return_pct,
                   spy_return_pct, alpha, buys_json, sells_json, holds_json, watchlist_json,
                   executive_summary, generated_at
            FROM strategy_briefings
            WHERE id = %s
        """, (briefing_id,))
        briefing = cursor.fetchone()
    finally:
        deps.db.return_connection(conn)

    if not briefing:
        return jsonify({'error': 'Briefing not found'}), 404

    result = dict(briefing)
    if result.get('generated_at'):
        result['generated_at'] = result['generated_at'].isoformat()

    return jsonify(result)
