import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from agent_tools import ToolExecutor

class TestThesisTool:
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        # Mock get_lynch_analysis
        db.get_lynch_analysis.return_value = {
            'analysis_text': 'Mocked cached thesis content for NVDA',
            'character_id': 'lynch',
            'generated_at': datetime.now()
        }
        return db

    @pytest.fixture
    def tool_executor(self, mock_db):
        from agent_tools import ToolExecutor
        return ToolExecutor(mock_db, stock_context=None, stock_analyst=None)

    def test_get_stock_thesis_cached(self, tool_executor, mock_db):
        """Test that get_stock_thesis retrieves from cache correctly."""
        result = tool_executor.execute('get_stock_thesis', {
            'ticker': 'NVDA',
            'character': 'lynch'
        })

        assert result['ticker'] == 'NVDA'
        assert result['character'] == 'lynch'
        assert "Mocked cached thesis content" in result['thesis']
        
        # Verify Database.get_lynch_analysis was called
        mock_db.get_lynch_analysis.assert_called_once()
        args, kwargs = mock_db.get_lynch_analysis.call_args
        assert kwargs['character_id'] == 'lynch'

    def test_get_stock_thesis_not_cached(self, tool_executor, mock_db):
        """Test returning a helpful message when not in cache."""
        mock_db.get_lynch_analysis.return_value = None
        
        result = tool_executor.execute('get_stock_thesis', {
            'ticker': 'NVDA'
        })

        assert result['thesis'] is None
        assert 'No cached investment thesis found' in result['message']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
