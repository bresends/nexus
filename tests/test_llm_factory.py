import pytest
from src.services.LLM import LLMService

class MockOpenAIClient:
    class chat:
        class completions:
            @staticmethod
            def create(model, messages):
                class Message:
                    content = '{"content": "Hello!", "category": "general"}'
                class Response:
                    choices = [type('obj', (object,), {'message': Message()})]
                return Response()

@pytest.fixture
def env_vars():
    return {
        "LLM_API_KEY": "fake-key",
        "LLM_BASE_URL": "https://fake-url.com"
    }

def test_get_response(monkeypatch, env_vars):
    # Patch OpenAI in LLMService to use the mock
    import src.services.LLM as llm_module
    llm_module.OpenAI = lambda api_key, base_url: type('obj', (object,), {'chat': MockOpenAIClient.chat})

    service = llm_module.LLMService(env_vars)
    result = service.get_response("Hi there!")
    assert result == {"content": "Hello!", "category": "general"}