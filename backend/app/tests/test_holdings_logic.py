import pytest
from unittest.mock import MagicMock, patch
import json
import os

# Fixtures path
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')

def load_fixture(filename):
    with open(os.path.join(FIXTURES_DIR, filename), 'r') as f:
        return f.read()

@pytest.fixture
def deliberation_text_adp():
    return load_fixture('adp_deliberation.md')

@pytest.fixture
def thesis_text_adp():
    return load_fixture('adp_thesis.md')

@pytest.fixture
def thesis_text_acnb():
    return load_fixture('acnb_thesis.md')

@patch('database.core.ConnectionPool')
@patch.dict('os.environ', {'SKIP_SCHEMA_INIT': 'true'})
def test_get_holdings_reasoning_with_mocks(mock_pool, deliberation_text_adp, thesis_text_adp, thesis_text_acnb):
    """Test get_holdings_reasoning with mocked database results."""
    from database import Database
    
    # Setup mock DB
    db = Database(host='localhost', port=5432, database='test', user='lynch', password='password')
    mock_conn = MagicMock()
    db.get_connection = MagicMock(return_value=mock_conn)
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # 1. Test 2-Analyst Strategy (Deliberation)
    mock_cursor.fetchall.side_effect = [
        [{'symbol': 'ADP'}], # Held symbols
        [{'symbol': 'ADP', 'deliberation_text': deliberation_text_adp, 'final_verdict': 'BUY'}] # Deliberation
    ]
    mock_cursor.fetchone.side_effect = [
        {'conditions': json.dumps({"analysts": ["lynch", "buffett"]})}, # Strategy config
    ]
    
    result = db.get_holdings_reasoning(1)
    
    assert 'ADP' in result
    assert result['ADP']['thesis_summary'].startswith("While the valuation (P/E of 23.75) is on the higher side")
    assert result['ADP']['thesis_summary'].endswith("We recommend buying a partial position now and adding aggressively on any market-wide pullbacks.")
    assert result['ADP']['consensus_verdict'] == "BUY"

    # 2. Test 1-Analyst Strategy (Thesis)
    mock_cursor.fetchall.side_effect = [
        [{'symbol': 'ADP'}], # Held symbols
        [{'symbol': 'ADP', 'analysis_text': thesis_text_adp, 'character_id': 'lynch'}] # Thesis
    ]
    mock_cursor.fetchone.side_effect = [
        {'conditions': json.dumps({"analysts": ["lynch"]})}, # Strategy config
    ]
    
    result = db.get_holdings_reasoning(1)
    
    assert 'ADP' in result
    assert result['ADP']['thesis_summary'].startswith("ADP is the quintessential \"toll booth\" business, exhibiting a widening moat")
    assert result['ADP']['thesis_summary'].endswith("has reduced its share count by 22% since 2008 while doubling net margins.")
    assert result['ADP']['consensus_verdict'] == "BUY"

    # 3. Test 1-Analyst Strategy for ACNB (Thesis)
    mock_cursor.fetchall.side_effect = [
        [{'symbol': 'ACNB'}], # Held symbols
        [{'symbol': 'ACNB', 'analysis_text': thesis_text_acnb, 'character_id': 'lynch'}] # Thesis
    ]
    mock_cursor.fetchone.side_effect = [
        {'conditions': json.dumps({"analysts": ["lynch"]})}, # Strategy config
    ]
    
    result = db.get_holdings_reasoning(1)
    
    assert 'ACNB' in result
    assert result['ACNB']['thesis_summary'].startswith("ACNB is a classic Lynch \"Stalwart\" masquerading as a \"Slow Grower,\" currently trading at a disconnect")
    assert result['ACNB']['thesis_summary'].endswith("requires verification of margin recovery or accretive M&A integration before committing capital.")
    # assert result['ADP']['consensus_verdict'] == "BUY"


