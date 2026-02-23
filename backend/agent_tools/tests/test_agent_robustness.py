import pytest
from unittest.mock import MagicMock, patch
from smart_chat_agent import SmartChatAgent
from google.genai.types import Content, Part, GenerateContentConfig

class MockResponse:
    def __init__(self, text=None, function_calls=None):
        self.candidates = [MagicMock()]
        self.candidates[0].content = MagicMock()
        self.candidates[0].content.parts = []
        if text:
            part = MagicMock(spec=Part)
            part.text = text
            # Ensure it doesn't have function_call
            if hasattr(part, 'function_call'):
                part.function_call = None
            self.candidates[0].content.parts.append(part)
        if function_calls:
            for fc in function_calls:
                part = MagicMock(spec=Part)
                part.function_call = fc
                self.candidates[0].content.parts.append(part)
        self.text = text

def test_chat_retry_on_max_iterations():
    mock_db = MagicMock()
    agent = SmartChatAgent(mock_db, gemini_api_key='test')
    agent._client = MagicMock()
    
    # First call to generate_content should lead to max iterations
    # We'll mock it to return a function call every time
    mock_fc = MagicMock()
    mock_fc.name = 'get_stock_metrics'
    mock_fc.args = {'ticker': 'NVDA'}
    
    # Mock return value for get_stock_metrics
    agent.tool_executor.execute = MagicMock(return_value={'price': 100})
    
    # We want it to hit MAX_ITERATIONS (50)
    # So we'll return function calls 50 times, then on the 51st call (which is the retry), return a text response.
    responses = [MockResponse(function_calls=[mock_fc]) for _ in range(50)]
    responses.append(MockResponse(text="Final Answer after retry"))
    
    agent.client.models.generate_content.side_effect = responses
    
    result = agent.chat('NVDA', 'What is the price?')
    
    assert result['response'] == "Final Answer after retry"
    # Total iterations = 50 (first attempt) + 1 (retry successful on first step)
    # Wait, the way recursion works:
    # First call chat():
    #   Loop 50 times -> break -> retries_left > 0 -> return self.chat(..., retries_left=0)
    # Second call chat():
    #   Loop 1 time -> return result
    assert result['iterations'] == 1 
    assert agent.client.models.generate_content.call_count == 51

def test_chat_stream_temperature_and_retry():
    mock_db = MagicMock()
    agent = SmartChatAgent(mock_db, gemini_api_key='test')
    agent._client = MagicMock()
    
    # Mock generate_content to hit max iterations
    mock_fc = MagicMock()
    mock_fc.name = 'get_stock_metrics'
    mock_fc.args = {'ticker': 'NVDA'}
    
    agent.tool_executor.execute = MagicMock(return_value={'price': 100})
    
    # 50 function calls, then 1 final response
    responses = [MockResponse(function_calls=[mock_fc]) for _ in range(50)]
    responses.append(MockResponse(text="Final Answer"))
    
    agent.client.models.generate_content.side_effect = responses
    
    # Capture yields
    yields = list(agent.chat_stream('NVDA', 'What is the price?'))
    
    # Check for temperature setting in config
    call_args = agent.client.models.generate_content.call_args_list[0]
    config = call_args.kwargs['config']
    assert config.temperature == 0.3
    
    # Check for retry indicator in yields
    retry_indicators = [y for y in yields if y['type'] == 'thinking' and 'Max reasoning steps reached' in y['data']]
    assert len(retry_indicators) == 1
    
    # Check final done message
    done_msg = yields[-1]
    assert done_msg['type'] == 'done'
    assert done_msg['data']['iterations'] == 1 # iterations for the successful call

if __name__ == "__main__":
    test_chat_retry_on_max_iterations()
    test_chat_stream_temperature_and_retry()
    print("Tests passed!")
