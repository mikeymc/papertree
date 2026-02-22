import pytest
import os
from strategy_executor.thesis import ThesisMixin

class MockExecutor(ThesisMixin):
    def __init__(self):
        self.db = None # Mocking not needed for _extract_thesis_verdict

def test_extract_acnb_verdict():
    """
    Test that _extract_thesis_verdict correctly returns WATCH for the ACNB thesis
    """
    # Load ACNB thesis from fixture
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'acnb_thesis.md')
    with open(fixture_path, 'r') as f:
        acnb_thesis = f.read()
    
    executor = MockExecutor()
    verdict = executor._extract_thesis_verdict(acnb_thesis)
    
    print(f"\nExtracted verdict: {verdict}")
    
    assert verdict == "WATCH", f"Expected WATCH but got {verdict}"

def test_extract_simple_buy():
    executor = MockExecutor()
    assert executor._extract_thesis_verdict("## Bottom Line: **BUY**\nGreat company.") == "BUY"

def test_extract_simple_watch():
    executor = MockExecutor()
    assert executor._extract_thesis_verdict("## Bottom Bottom Line: **WATCH**\nMaybe later.") == "WATCH"

def test_extract_simple_avoid():
    executor = MockExecutor()
    assert executor._extract_thesis_verdict("Verdict: AVOID. Garbage stock.") == "AVOID"
