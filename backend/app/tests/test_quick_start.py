# ABOUTME: Tests for the quick-start onboarding endpoint
# ABOUTME: Validates template-based strategy creation and job triggering

import pytest
from unittest.mock import patch, MagicMock


class TestQuickStartEndpoint:
    """Tests for POST /api/strategies/quick-start."""

    @pytest.fixture
    def client(self, test_database):
        """Flask test client with authenticated session."""
        import os
        import sys

        os.environ['DB_NAME'] = test_database
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_USER'] = 'lynch'
        os.environ['DB_PASSWORD'] = 'lynch_dev_password'
        os.environ['DEV_AUTH_BYPASS'] = '1'

        from app import app
        app.config['TESTING'] = True

        with app.test_client() as client:
            # Simulate authenticated session
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            yield client

    @pytest.fixture
    def seed_user(self, test_database):
        """Create a test user in the database."""
        import psycopg
        conn = psycopg.connect(
            dbname=test_database,
            user='lynch',
            password='lynch_dev_password',
            host='localhost',
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, email, name, is_verified, has_completed_onboarding)
            VALUES (1, 'test@example.com', 'Test User', true, true)
            ON CONFLICT (id) DO NOTHING
        """)
        conn.commit()
        cursor.close()
        conn.close()

    def test_quick_start_creates_strategy_and_portfolio(self, client, seed_user):
        """Quick-start should create a strategy, portfolio, and trigger a job."""
        with patch('app.strategies.deps') as mock_deps, \
             patch('app.strategies.get_fly_manager') as mock_fly:
            mock_deps.db.create_portfolio.return_value = 42
            mock_deps.db.create_strategy.return_value = 7
            mock_deps.db.create_background_job.return_value = 99
            mock_deps.db.get_pool_stats.return_value = {'usage_percent': 10}
            mock_fly.return_value.start_worker_for_job.return_value = 'worker-1'

            response = client.post('/api/strategies/quick-start', json={
                'template_id': 'dream_team'
            })

            assert response.status_code == 201
            data = response.get_json()
            assert data['strategy_id'] == 7
            assert data['portfolio_id'] == 42
            assert data['job_id'] == 99

    def test_quick_start_uses_template_config(self, client, seed_user):
        """Quick-start should pass the correct template config to create_strategy."""
        with patch('app.strategies.deps') as mock_deps, \
             patch('app.strategies.get_fly_manager') as mock_fly:
            mock_deps.db.create_portfolio.return_value = 1
            mock_deps.db.create_strategy.return_value = 1
            mock_deps.db.create_background_job.return_value = 1
            mock_deps.db.get_pool_stats.return_value = {'usage_percent': 10}
            mock_fly.return_value.start_worker_for_job.return_value = 'w-1'

            client.post('/api/strategies/quick-start', json={
                'template_id': 'dream_team'
            })

            # Verify create_strategy was called with template config values
            call_kwargs = mock_deps.db.create_strategy.call_args
            assert call_kwargs.kwargs['consensus_mode'] == 'both_agree'
            assert call_kwargs.kwargs['consensus_threshold'] == 70.0
            assert call_kwargs.kwargs['schedule_cron'] == '0 9 * * 1-5'

    def test_quick_start_enables_strategy(self, client, seed_user):
        """Quick-start strategy should be enabled for scheduled runs."""
        with patch('app.strategies.deps') as mock_deps, \
             patch('app.strategies.get_fly_manager') as mock_fly:
            mock_deps.db.create_portfolio.return_value = 1
            mock_deps.db.create_strategy.return_value = 5
            mock_deps.db.create_background_job.return_value = 1
            mock_deps.db.update_strategy.return_value = True
            mock_deps.db.get_pool_stats.return_value = {'usage_percent': 10}
            mock_fly.return_value.start_worker_for_job.return_value = 'w-1'

            client.post('/api/strategies/quick-start', json={
                'template_id': 'buffett_fortress'
            })

            # Strategy should be enabled after creation
            mock_deps.db.update_strategy.assert_called_once()
            enable_kwargs = mock_deps.db.update_strategy.call_args
            assert enable_kwargs.kwargs['enabled'] is True

    def test_quick_start_rejects_unknown_template(self, client, seed_user):
        """Should return 400 for unknown template_id."""
        response = client.post('/api/strategies/quick-start', json={
            'template_id': 'nonexistent_template'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_quick_start_rejects_missing_template_id(self, client, seed_user):
        """Should return 400 when template_id is missing."""
        response = client.post('/api/strategies/quick-start', json={})

        assert response.status_code == 400

    def test_quick_start_requires_auth(self, test_database):
        """Should return 401 when not authenticated."""
        import os
        import sys
        import auth

        os.environ['DB_NAME'] = test_database

        from app import app
        app.config['TESTING'] = True

        # DEV_AUTH_BYPASS is computed at import time, so patch it directly
        original_bypass = auth.DEV_AUTH_BYPASS
        auth.DEV_AUTH_BYPASS = False
        try:
            with app.test_client() as client:
                response = client.post('/api/strategies/quick-start', json={
                    'template_id': 'buffett_fortress'
                })
                # Should return 401 when not authenticated
                assert response.status_code == 401
        finally:
            auth.DEV_AUTH_BYPASS = original_bypass

    def test_quick_start_triggers_strategy_execution_job(self, client, seed_user):
        """Quick-start should create a strategy_execution job for the new strategy."""
        with patch('app.strategies.deps') as mock_deps, \
             patch('app.strategies.get_fly_manager') as mock_fly:
            mock_deps.db.create_portfolio.return_value = 1
            mock_deps.db.create_strategy.return_value = 10
            mock_deps.db.create_background_job.return_value = 50
            mock_deps.db.update_strategy.return_value = True
            mock_deps.db.get_pool_stats.return_value = {'usage_percent': 10}
            mock_fly.return_value.start_worker_for_job.return_value = 'w-1'

            client.post('/api/strategies/quick-start', json={
                'template_id': 'small_cap_gems'
            })

            # Should create a strategy_execution job targeting the new strategy
            mock_deps.db.create_background_job.assert_called_once()
            job_call = mock_deps.db.create_background_job.call_args
            assert job_call.args[0] == 'strategy_execution'
            assert job_call.args[1]['strategy_ids'] == [10]


class TestQuickStartConfigs:
    """Tests for QUICK_START_CONFIGS data integrity."""

    def test_all_templates_have_quick_start_configs(self):
        """Every filter template should have a corresponding quick-start config."""
        from strategy_templates import FILTER_TEMPLATES, QUICK_START_CONFIGS
        for template_id in FILTER_TEMPLATES:
            assert template_id in QUICK_START_CONFIGS, \
                f"Missing quick-start config for template: {template_id}"

    def test_quick_start_configs_have_required_fields(self):
        """Each quick-start config must have all fields needed to create a strategy."""
        from strategy_templates import QUICK_START_CONFIGS
        required_fields = [
            'name', 'description', 'conditions', 'consensus_mode',
            'consensus_threshold', 'position_sizing', 'exit_conditions',
            'schedule_cron', 'initial_cash'
        ]
        for template_id, config in QUICK_START_CONFIGS.items():
            for field in required_fields:
                assert field in config, \
                    f"Missing field '{field}' in quick-start config: {template_id}"

    def test_quick_start_configs_have_valid_filters(self):
        """Each quick-start config's conditions should contain filters."""
        from strategy_templates import QUICK_START_CONFIGS
        for template_id, config in QUICK_START_CONFIGS.items():
            assert 'filters' in config['conditions'], \
                f"Missing filters in conditions for: {template_id}"
            assert len(config['conditions']['filters']) > 0, \
                f"Empty filters for: {template_id}"

    def test_character_recommendations_reference_valid_templates(self):
        """CHARACTER_RECOMMENDATIONS should only reference existing templates."""
        from strategy_templates import CHARACTER_RECOMMENDATIONS, QUICK_START_CONFIGS
        for character, templates in CHARACTER_RECOMMENDATIONS.items():
            for template_id in templates:
                assert template_id in QUICK_START_CONFIGS, \
                    f"Character '{character}' recommends unknown template: {template_id}"
