# ABOUTME: Investment strategy CRUD and execution endpoints
# ABOUTME: Handles strategy creation, previews, and template listing

from flask import Blueprint, jsonify, request, session
from app import deps
from auth import require_user_auth
import logging

logger = logging.getLogger(__name__)

strategies_bp = Blueprint('strategies', __name__)


@strategies_bp.route('/api/strategies', methods=['POST'])
@require_user_auth
def create_strategy(user_id):
    """Create a new investment strategy."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        name = data.get('name')
        if not name:
            return jsonify({'error': 'Name is required'}), 400

        # Handle Portfolio creation if needed
        portfolio_id = data.get('portfolio_id')
        if portfolio_id == 'new':
            # Create new portfolio with same name
            # Defaulting to 100k cash as per standard practice
            portfolio_id = deps.db.create_portfolio(user_id, name, initial_cash=100000.0)

        strategy_id = deps.db.create_strategy(
            user_id=user_id,
            portfolio_id=portfolio_id,
            name=name,
            description=data.get('description'),
            conditions=data.get('conditions', {}),
            consensus_mode=data.get('consensus_mode', 'both_agree'),
            consensus_threshold=float(data.get('consensus_threshold', 70.0)),
            position_sizing=data.get('position_sizing'),
            exit_conditions=data.get('exit_conditions'),
            schedule_cron=data.get('schedule_cron', '0 9 * * 1-5')
        )

        return jsonify({
            'id': strategy_id,
            'message': 'Strategy created successfully',
            'portfolio_id': portfolio_id
        }), 201

    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        return jsonify({'error': str(e)}), 500


@strategies_bp.route('/api/strategies/<int:strategy_id>', methods=['PUT'])
@require_user_auth
def update_strategy(user_id, strategy_id):
    """Update an existing investment strategy."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Verify ownership
        strategy = deps.db.get_strategy(strategy_id)
        if not strategy:
            return jsonify({'error': 'Strategy not found'}), 404
        
        is_admin = session.get('user_type') == 'admin'
        if strategy['user_id'] != user_id and not is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        success = deps.db.update_strategy(
            user_id=user_id,
            strategy_id=strategy_id,
            name=data.get('name'),
            description=data.get('description'),
            conditions=data.get('conditions'),
            consensus_mode=data.get('consensus_mode'),
            consensus_threshold=float(data.get('consensus_threshold')) if data.get('consensus_threshold') else None,
            position_sizing=data.get('position_sizing'),
            exit_conditions=data.get('exit_conditions'),
            schedule_cron=data.get('schedule_cron'),
            portfolio_id=data.get('portfolio_id'),
            enabled=data.get('enabled')
        )

        if success:
            return jsonify({'message': 'Strategy updated successfully'})
        else:
            return jsonify({'error': 'No changes made or update failed'}), 400

    except Exception as e:
        logger.error(f"Error updating strategy: {e}")
        return jsonify({'error': str(e)}), 500


@strategies_bp.route('/api/strategies', methods=['GET'])
@require_user_auth
def get_strategies(user_id):
    """Get all investment strategies for the current user."""
    try:
        strategies = deps.db.get_user_strategies(user_id)
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'error': str(e)}), 500


@strategies_bp.route('/api/strategies/<int:strategy_id>', methods=['GET'])
@require_user_auth
def get_strategy_detail(user_id, strategy_id):
    """Get detailed strategy info including performance and recent runs."""
    try:
        strategy = deps.db.get_strategy(strategy_id)
        if not strategy:
            return jsonify({'error': 'Strategy not found'}), 404

        is_admin = session.get('user_type') == 'admin'
        logger.info(f"[AUTH DEBUG] Strategy detail access: user_id={user_id} (type={type(user_id)}), strategy_owner={strategy['user_id']} (type={type(strategy['user_id'])}), is_admin={is_admin}")
        
        if strategy['user_id'] != user_id and not is_admin:
            logger.warning(f"[AUTH DEBUG] Access DENIED for user {user_id} to strategy {strategy_id}")
            return jsonify({'error': 'Unauthorized'}), 403

        # Get performance series
        performance = deps.db.get_strategy_performance(strategy_id)

        # Get recent runs
        runs = deps.db.get_strategy_runs(strategy_id, limit=20)

        return jsonify({
            'strategy': strategy,
            'performance': performance,
            'runs': runs
        })
    except Exception as e:
        logger.error(f"Error getting strategy detail: {e}")
        return jsonify({'error': str(e)}), 500




@strategies_bp.route('/api/strategies/runs/<int:run_id>/decisions', methods=['GET'])
@require_user_auth
def get_run_decisions(user_id, run_id):
    """Get decisions for a specific strategy run."""
    try:
        # Verify ownership via strategy -> run -> decision chain
        # Use a join or two-step lookup. For now, simple lookup.
        run = deps.db.get_strategy_run(run_id)
        if not run:
            return jsonify({'error': 'Run not found'}), 404

        strategy = deps.db.get_strategy(run['strategy_id'])
        is_admin = session.get('user_type') == 'admin'
        if not strategy or (strategy['user_id'] != user_id and not is_admin):
             return jsonify({'error': 'Unauthorized'}), 403

        decisions = deps.db.get_run_decisions(run_id)
        return jsonify(decisions)
    except Exception as e:
        logger.error(f"Error getting run decisions: {e}")
        return jsonify({'error': str(e)}), 500


@strategies_bp.route('/api/strategy-templates', methods=['GET'])
def get_strategy_templates():
    """Get available strategy templates for wizard and chat."""
    from strategy_templates import FILTER_TEMPLATES
    return jsonify({
        'templates': {
            k: {
                'name': v['name'],
                'description': v['description'],
                'filters': v['filters']
            }
            for k, v in FILTER_TEMPLATES.items()
        }
    })
