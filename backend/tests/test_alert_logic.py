import pytest
import sys
import os
import json
import logging
import traceback
from typing import Dict, Any, List


# sys.path handled by conftest.py

try:
    from worker import BackgroundWorker
except ImportError:
    # This might happen during collection if path not set, but conftest should handle it
    pass

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def load_test_cases(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r') as f:
        return json.load(f)


def test_alert_logic():
    """Test LLM alert construction and triggering logic."""
    logger.info("Initializing BackgroundWorker...")
    worker = BackgroundWorker()

    test_file = os.path.join(os.path.dirname(__file__), 'scenarios/alert_test_cases.json')
    assert os.path.exists(test_file), f"Test cases not found at {test_file}"

    cases = load_test_cases(test_file)
    logger.info(f"Loaded {len(cases)} test cases.")

    passed = 0
    failed_cases = []

    for i, case in enumerate(cases):
        symbol = case['metrics'].get('symbol', 'TEST')
        condition = case['condition']
        metrics = case['metrics']
        context = case.get('context')

        try:
            # 1. Construct Prompt
            prompt = worker._construct_alert_prompt(symbol, condition, metrics, context)
            
            # 2. Call LLM (mocking the exact call structure from worker.py)
            response = worker.llm_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            
            result = json.loads(response.text)
            triggered = result.get('triggered', False)
            reason = result.get('reason', '')
            
            # 3. Verify
            expected_trigger = case['expected_trigger']
            trigger_match = (triggered == expected_trigger)
            
            reason_match = True
            if 'expected_reason_contains' in case:
                if case['expected_reason_contains'].lower() not in reason.lower():
                    reason_match = False

            if trigger_match and reason_match:
                passed += 1
            else:
                failed_cases.append({
                    'id': case['id'],
                    'expected': expected_trigger,
                    'got': triggered,
                    'reason': reason
                })
            
            # Avoid rate limits
            import time
            time.sleep(1) # Reduced sleep for tests

        except Exception as e:
            failed_cases.append({
                'id': case['id'],
                'error': str(e)
            })

    if failed_cases:
        pytest.fail(f"Alert logic tests failed: {failed_cases}")
