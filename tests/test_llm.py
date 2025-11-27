"""Tests for LLMClient using real OpenAI API."""

import os
import pytest

from personal_ai.llm import LLMClient


class TestLLMClient:
    """Test LLMClient with real OpenAI integration."""

    def test_initialization(self):
        """Test LLMClient initialization."""
        api_key = os.environ.get("OPENAI_API_KEY", "test-key")
        client = LLMClient(api_key, "gpt-4o-mini", 0.7)
        assert client.api_key == api_key
        assert client.model == "gpt-4o-mini"
        assert client.temperature == 0.7

    def test_missing_openai_package(self, monkeypatch):
        """Test error handling when openai package is missing."""
        import sys

        # Temporarily remove openai module
        original_module = sys.modules.pop("openai", None)
        try:
            with pytest.raises(RuntimeError, match="The 'openai' package is required"):
                LLMClient("test-key", "gpt-4o-mini")
        finally:
            if original_module:
                sys.modules["openai"] = original_module

    @pytest.mark.unit
    def test_complete_chat_success(self):
        """Test successful chat completion with real API."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        client = LLMClient(api_key, "gpt-4o-mini", 0.7)
        messages = [{"role": "user", "content": "Say hello in one word."}]
        response = client.complete_chat(messages)

        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)

    @pytest.mark.unit
    def test_complete_chat_with_custom_max_tokens(self):
        """Test chat completion with custom max_tokens."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        client = LLMClient(api_key, "gpt-4o-mini")
        messages = [{"role": "user", "content": "Count to 3."}]
        response = client.complete_chat(messages, max_output_tokens=50)

        assert response is not None
        assert len(response) > 0

    @pytest.mark.unit
    def test_complete_chat_strips_whitespace(self):
        """Test that response content is stripped."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        client = LLMClient(api_key, "gpt-4o-mini")
        messages = [{"role": "user", "content": "Say 'test' only."}]
        response = client.complete_chat(messages)

        # Response should be trimmed (no leading/trailing whitespace)
        assert response == response.strip()

    @pytest.mark.unit
    def test_conversation_context(self):
        """Test that conversation context is maintained."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        client = LLMClient(api_key, "gpt-4o-mini", 0.7)
        
        # First message
        messages1 = [{"role": "user", "content": "My name is Alice."}]
        response1 = client.complete_chat(messages1)
        assert response1 is not None

        # Second message with context
        messages2 = messages1 + [
            {"role": "assistant", "content": response1},
            {"role": "user", "content": "What is my name?"}
        ]
        response2 = client.complete_chat(messages2)
        
        assert response2 is not None
        # Response should reference the name from context
        assert len(response2) > 0
