# ABOUTME: Investment strategy CRUD and execution endpoints
# ABOUTME: Handles strategy creation, previews, and template listing

from flask import Blueprint, jsonify, request, session
from app import deps
from auth import require_user_auth
from fly_machines import get_fly_manager
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

        initial_cash = data.get('initial_cash', 100000.0)
        try:
            initial_cash = float(initial_cash)
        except (ValueError, TypeError):
            initial_cash = 100000.0

        # Handle Portfolio creation if needed
        portfolio_id = data.get('portfolio_id')
        if portfolio_id == 'new':
            # Create new portfolio with same name
            portfolio_id = deps.db.create_portfolio(user_id, name, initial_cash=initial_cash)

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


@strategies_bp.route('/api/strategies/quick-start', methods=['POST'])
@require_user_auth
def quick_start_strategy(user_id):
    """Create a strategy from a template and trigger its first run."""
    from strategy_templates import QUICK_START_CONFIGS

    try:
        data = request.json
        if not data or not data.get('template_id'):
            return jsonify({'error': 'template_id is required'}), 400

        template_id = data['template_id']
        if template_id not in QUICK_START_CONFIGS:
            return jsonify({'error': f'Unknown template: {template_id}'}), 400

        config = QUICK_START_CONFIGS[template_id]

        # Create portfolio
        portfolio_id = deps.db.create_portfolio(
            user_id, config['name'], initial_cash=config['initial_cash']
        )

        # Create strategy with template config
        strategy_id = deps.db.create_strategy(
            user_id=user_id,
            portfolio_id=portfolio_id,
            name=config['name'],
            description=config['description'],
            conditions=config['conditions'],
            consensus_mode=config['consensus_mode'],
            consensus_threshold=config['consensus_threshold'],
            position_sizing=config['position_sizing'],
            exit_conditions=config['exit_conditions'],
            schedule_cron=config['schedule_cron']
        )

        # Enable for scheduled runs
        deps.db.update_strategy(
            user_id=user_id,
            strategy_id=strategy_id,
            enabled=True
        )

        # Trigger first run immediately
        job_id = deps.db.create_background_job(
            'strategy_execution',
            {'strategy_ids': [strategy_id]},
            tier='light'
        )

        fly_manager = get_fly_manager()
        fly_manager.start_worker_for_job(tier='light', max_workers=4)

        return jsonify({
            'strategy_id': strategy_id,
            'portfolio_id': portfolio_id,
            'job_id': job_id
        }), 201

    except Exception as e:
        logger.error(f"Error in quick-start: {e}")
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
    from strategy_templates import FILTER_TEMPLATES, CHARACTER_RECOMMENDATIONS
    return jsonify({
        'templates': {
            k: {
                'name': v['name'],
                'description': v['description'],
                'filters': v['filters']
            }
            for k, v in FILTER_TEMPLATES.items()
        },
        'character_recommendations': CHARACTER_RECOMMENDATIONS
    })
