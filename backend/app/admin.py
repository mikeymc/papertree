from flask import Blueprint, jsonify, request, session
from app import deps
from auth import require_user_auth
import logging
from datetime import datetime, timedelta
import psycopg.rows
import yaml
import os
import re

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    """Decorator to require admin user_type"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = deps.db.get_user_by_id(session['user_id'])
        if not user or user.get('user_type') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/api/admin/ping', methods=['GET'])
def admin_ping():
    """Simple diagnostic endpoint to verify backend update"""
    return jsonify({
        'status': 'ok',
        'version': 'v1.1-schedule-refined',
        'has_yaml': 'yaml' in globals() or 'yaml' in locals()
    })


@admin_bp.route('/api/admin/conversations', methods=['GET'])
@require_admin
def get_conversations():
    """Get all conversations for admin review"""
    try:
        conn = deps.db.get_connection()
        try:
            cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
            # Join with users to get user details
            # agent_conversations replaces conversations
            cursor.execute("""
                SELECT c.*, u.email as user_email, u.name as user_name 
                FROM agent_conversations c
                JOIN users u ON c.user_id = u.id
                ORDER BY c.last_message_at DESC
                LIMIT 100
            """)
            conversations = [dict(row) for row in cursor.fetchall()]
            return jsonify({'conversations': conversations})
        finally:
            deps.db.return_connection(conn)
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/conversations/<conversation_id>/messages', methods=['GET'])
@require_admin
def get_conversation_messages(conversation_id):
    """Get messages for a specific conversation (read-only)"""
    try:
        conn = deps.db.get_connection()
        try:
            cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
            cursor.execute("""
                SELECT * FROM agent_messages 
                WHERE conversation_id = %s 
                ORDER BY created_at ASC
            """, (conversation_id,))
            messages = [dict(row) for row in cursor.fetchall()]
            return jsonify({'messages': messages})
        finally:
            deps.db.return_connection(conn)
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/strategies', methods=['GET'])
@require_admin
def get_all_strategies():
    """Get all strategies across all users"""
    try:
        conn = deps.db.get_connection()
        try:
            cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
            cursor.execute("""
                SELECT s.*, u.email as user_email, p.name as portfolio_name
                FROM investment_strategies s
                JOIN users u ON s.user_id = u.id
                LEFT JOIN portfolios p ON s.portfolio_id = p.id
                ORDER BY s.created_at DESC
            """)
            strategies = [dict(row) for row in cursor.fetchall()]
            return jsonify({'strategies': strategies})
        finally:
            deps.db.return_connection(conn)
    except Exception as e:
        logger.error(f"Error fetching strategies: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/portfolios', methods=['GET'])
@require_admin
def get_all_portfolios():
    """Get all portfolios across all users with computed values"""
    try:
        enriched_portfolios = deps.db.get_enriched_portfolios()
        return jsonify({'portfolios': enriched_portfolios})
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/admin/job_stats', methods=['GET'])
@require_admin
def get_job_stats():
    """Get aggregated background job statistics and timeline data"""
    try:
        hours = int(request.args.get('hours', 24))
        job_type = request.args.get('job_type', 'all')
        
        conn = deps.db.get_connection()
        try:
            cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
            time_threshold = datetime.now() - timedelta(hours=hours)
            
            # 1. Get stats by job type
            cursor.execute("""
                SELECT 
                    job_type,
                    tier,
                    COUNT(*) as total_runs,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_runs,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed_runs,
                    COUNT(*) FILTER (WHERE status = 'running') as running_runs,
                    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) FILTER (
                        WHERE status = 'completed' AND started_at IS NOT NULL AND completed_at IS NOT NULL
                    ) as avg_duration_seconds,
                    MAX(created_at) as last_run
                FROM background_jobs
                WHERE created_at >= %s
                GROUP BY job_type, tier
                ORDER BY total_runs DESC
            """, (time_threshold,))
            stats = [dict(row) for row in cursor.fetchall()]
            
            # 2. Get recent jobs (all jobs in timeframe, but limited to last 1000 for safety)
            query = """
                SELECT * FROM background_jobs
                WHERE created_at >= %s
            """
            params = [time_threshold]
            
            if job_type != 'all':
                query += " AND job_type = %s"
                params.append(job_type)
                
            query += " ORDER BY created_at DESC LIMIT 1000"
            
            cursor.execute(query, params)
            jobs = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'stats': stats,
                'jobs': jobs,
                'time_range': hours
            })
        finally:
            deps.db.return_connection(conn)
    except Exception as e:
        logger.error(f"Error fetching job stats: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/job_schedule', methods=['GET'])
@require_admin
def get_job_schedule():
    """Parse .github/workflows/scheduled-jobs.yml to return the job schedule"""
    try:
        # Resolve path to the workflow file
        # In local dev: it's root/.github/... and we are in root/backend/app/admin.py
        # In Docker: it's /app/.github/... and we are in /app/app/admin.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Try both locations
        paths_to_try = [
            os.path.join(os.path.dirname(base_dir), '.github/workflows/scheduled-jobs.yml'), # Local: root/.github
            os.path.join(base_dir, '.github/workflows/scheduled-jobs.yml'),               # Docker: /app/.github
            '.github/workflows/scheduled-jobs.yml'                                         # Fallback
        ]
        
        yaml_path = None
        for path in paths_to_try:
            if os.path.exists(path):
                yaml_path = path
                break
        
        if not yaml_path:
            logger.error(f"Schedule file not found in any of: {paths_to_try}")
            return jsonify({'error': 'Schedule file not found'}), 404
            
        with open(yaml_path, 'r') as f:
            content = f.read()
            data = yaml.safe_load(content)
            
        # Extract crons from the 'on' section
        on_block = data.get('on') or data.get(True)
        crons = on_block.get('schedule', []) if on_block else []
        cron_list = [c.get('cron') for c in crons if c.get('cron')]
        
        # Extract job type mapping
        mapping = {}
        case_block = re.search(r'case "\$SCHEDULE" in(.*?)\sesac', content, re.DOTALL)
        if case_block:
            case_content = case_block.group(1)
            matches = re.finditer(r'"(.*?)"\)\s+echo "type=(.*?)"', case_content)
            for m in matches:
                mapping[m.group(1)] = m.group(2)
        
        # Group by job type
        grouped_jobs = {}
        for cron in cron_list:
            job_type = mapping.get(cron, 'unknown')
            if job_type not in grouped_jobs:
                grouped_jobs[job_type] = {
                    'job_type': job_type,
                    'crons': [],
                    'description': get_job_description(job_type)
                }
            grouped_jobs[job_type]['crons'].append(cron)
        
        # Build the final schedule objects with EST conversion
        schedule = []
        for job_type, job_data in grouped_jobs.items():
            est_times = []
            frequencies = set()
            
            for cron in job_data['crons']:
                # Simple human readable frequency
                freq = "Custom"
                if cron == '0 * * * *': freq = "Hourly"
                elif cron.startswith('*/5'): freq = "Every 5 mins"
                elif cron.endswith('* * *'): freq = "Daily"
                elif '1-5' in cron or '2-6' in cron: freq = "Weekdays"
                frequencies.add(freq)
                
                # Convert to EST
                est_times.append(cron_to_est(cron))
            
            # Sort EST times (roughly)
            # This is tricky because they are strings like "6a", "12p"
            # We'll just keep them in order of appearance for now
            
            schedule.append({
                'job_type': job_type,
                'est_times': ", ".join(est_times),
                'frequency': "/".join(sorted(list(frequencies))),
                'cron': ", ".join(job_data['crons']),
                'description': job_data['description']
            })
            
        return jsonify({'schedule': schedule})
    except Exception as e:
        logger.error(f"Error fetching job schedule: {e}")
        return jsonify({'error': str(e)}), 500

def cron_to_est(cron):
    """Simple conversion of UTC cron to EST (UTC-5) human time"""
    if cron == '*/5 * * * *': return "Every 5m"
    if cron == '0 * * * *': return "Hourly (:00)"
    
    parts = cron.split()
    if len(parts) < 2: return cron
    
    try:
        minute = int(parts[0])
        hour_utc = int(parts[1])
        
        # Convert UTC to EST (UTC-5)
        hour_est = (hour_utc - 5) % 24
        
        # Format as 6a, 12p, etc.
        suffix = 'a' if hour_est < 12 else 'p'
        display_hour = hour_est if hour_est <= 12 else hour_est - 12
        if display_hour == 0: display_hour = 12
        
        time_str = f"{display_hour}"
        if minute > 0:
            time_str += f":{minute:02d}"
        time_str += suffix
        
        return time_str
    except (ValueError, IndexError):
        return cron

def get_job_description(job_type):
    """Helper to provide descriptions for job types"""
    descriptions = {
        'price_update': 'Fast fetch of latest stock prices from TradingView',
        'check_alerts': 'Evaluate user alerts against latest price/data changes',
        'full_screening': 'Daily deep screen of the entire market universe',
        'news_cache': 'Refresh news items for followed or quality stocks',
        '8k_cache': 'Fetch latest SEC 8-K filings',
        '10k_cache': 'Fetch latest SEC 10-K/10-Q filings',
        'form4_cache': 'Fetch latest Form 4 (insider trading) filings',
        'price_history_cache': 'Update historical price series for charting',
        'outlook_cache': 'Fetch analyst outlook and price targets',
        'transcript_cache': 'Fetch and process earnings call transcripts',
        'forward_metrics_cache': 'Calculate forward-looking valuation metrics',
        'thesis_refresher': 'Regenerate AI investment theses for quality stocks',
        'strategy_execution': 'Execute autonomous trading strategies',
        'benchmark_snapshot': 'Record daily S&P 500 closing prices',
        'portfolio_sweep': 'Process dividends and record portfolio snapshots'
    }
    return descriptions.get(job_type, 'No description provided')

@admin_bp.route('/api/admin/user_actions', methods=['GET'])
@require_admin
def get_user_actions():
    """Get recent user actions/events and user stats"""
    try:
        conn = deps.db.get_connection()
        try:
            cursor = conn.cursor(row_factory=psycopg.rows.dict_row)
            
            # 1. Get recent events (existing logic)
            cursor.execute("""
                SELECT ue.*, u.email as user_email, u.name as user_name 
                FROM user_events ue
                LEFT JOIN users u ON ue.user_id = u.id
                ORDER BY ue.created_at DESC
                LIMIT 100
            """)
            events = [dict(row) for row in cursor.fetchall()]
            
            # 2. Get aggregate user stats
            cursor.execute("""
                SELECT 
                    u.id as user_id,
                    u.email,
                    u.name,
                    COUNT(ue.id) as total_hits,
                    MAX(ue.created_at) as last_activity
                FROM users u
                LEFT JOIN user_events ue ON u.id = ue.user_id
                GROUP BY u.id, u.email, u.name
                ORDER BY total_hits DESC
            """)
            stats = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'events': events,
                'stats': stats
            })
        finally:
            deps.db.return_connection(conn)
    except Exception as e:
        logger.error(f"Error fetching user events: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/feedback', methods=['GET'])
@require_admin
def get_all_feedback():
    """Get all user feedback for admin review"""
    try:
        feedback = deps.db.get_all_feedback()
        return jsonify({'feedback': feedback})
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        return jsonify({'error': str(e)}), 500
