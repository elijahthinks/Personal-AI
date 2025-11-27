"""Tests for MemoryStore."""

import json
from pathlib import Path

import pytest

from personal_ai.memory import MemoryStore, MemoryState


class TestMemoryState:
    """Test MemoryState dataclass."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        state = MemoryState(
            conversation=[{"role": "user", "content": "Hello"}],
            summary="Test summary",
            user_profile={"name": "Test"},
            reflections=["Reflection 1"],
        )
        data = state.to_dict()
        assert data["conversation"] == [{"role": "user", "content": "Hello"}]
        assert data["summary"] == "Test summary"
        assert data["user_profile"] == {"name": "Test"}
        assert data["reflections"] == ["Reflection 1"]

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "conversation": [{"role": "user", "content": "Hello"}],
            "summary": "Test summary",
            "user_profile": {"name": "Test"},
            "reflections": ["Reflection 1"],
        }
        state = MemoryState.from_dict(data)
        assert len(state.conversation) == 1
        assert state.summary == "Test summary"
        assert state.user_profile == {"name": "Test"}
        assert len(state.reflections) == 1


class TestMemoryStore:
    """Test MemoryStore persistence and operations."""

    def test_initialization_creates_empty_store(self, memory_path: Path):
        """Test that a new MemoryStore starts empty."""
        store = MemoryStore(memory_path)
        assert store.conversation_length() == 0
        assert store.get_summary() == ""
        assert store.get_user_profile() == {}
        assert store.get_reflections() == []

    def test_persists_messages(self, memory_path: Path):
        """Test that messages are saved to disk."""
        store = MemoryStore(memory_path)
        store.add_message("user", "Hello")
        store.add_message("assistant", "Hi there")

        # Create a new store instance to verify persistence
        new_store = MemoryStore(memory_path)
        assert new_store.conversation_length() == 2
        recent = new_store.get_recent(10)
        assert recent[0]["role"] == "user"
        assert recent[0]["content"] == "Hello"
        assert recent[1]["role"] == "assistant"
        assert recent[1]["content"] == "Hi there"

    def test_loads_existing_data(self, memory_path: Path):
        """Test loading existing memory from file."""
        data = {
            "conversation": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Response"},
            ],
            "summary": "Old summary",
            "user_profile": {"key": "value"},
            "reflections": ["Note 1", "Note 2"],
        }
        memory_path.write_text(json.dumps(data))

        store = MemoryStore(memory_path)
        assert store.conversation_length() == 2
        assert store.get_summary() == "Old summary"
        assert store.get_user_profile() == {"key": "value"}
        assert len(store.get_reflections()) == 2

    def test_get_recent_with_limit(self, memory_path: Path):
        """Test getting recent messages with a limit."""
        store = MemoryStore(memory_path)
        for i in range(10):
            store.add_message("user", f"Message {i}")

        recent = store.get_recent(5)
        assert len(recent) == 5
        assert recent[-1]["content"] == "Message 9"

    def test_get_recent_without_limit(self, memory_path: Path):
        """Test getting all messages when limit is 0 or negative."""
        store = MemoryStore(memory_path)
        for i in range(5):
            store.add_message("user", f"Message {i}")

        all_messages = store.get_recent(0)
        assert len(all_messages) == 5

    def test_add_reflection(self, memory_path: Path):
        """Test adding reflections."""
        store = MemoryStore(memory_path)
        store.add_reflection("Test reflection")
        assert len(store.get_reflections()) == 1
        assert store.get_reflections()[0] == "Test reflection"

        # Verify persistence
        new_store = MemoryStore(memory_path)
        assert len(new_store.get_reflections()) == 1

    def test_update_user_profile(self, memory_path: Path):
        """Test updating user profile."""
        store = MemoryStore(memory_path)
        store.update_user_profile("name", "Alice")
        store.update_user_profile("age", "30")

        profile = store.get_user_profile()
        assert profile["name"] == "Alice"
        assert profile["age"] == "30"

        # Verify persistence
        new_store = MemoryStore(memory_path)
        assert new_store.get_user_profile()["name"] == "Alice"

    def test_should_summarize(self, memory_path: Path):
        """Test summary threshold check."""
        store = MemoryStore(memory_path)
        assert not store.should_summarize(16)

        for i in range(16):
            store.add_message("user", f"Message {i}")

        assert store.should_summarize(16)
        assert not store.should_summarize(20)

    def test_handles_corrupted_json(self, memory_path: Path):
        """Test graceful handling of corrupted JSON."""
        memory_path.write_text("{ invalid json }")
        store = MemoryStore(memory_path)
        # Should start with empty state
        assert store.conversation_length() == 0

    @pytest.mark.unit
    def test_update_summary_with_real_llm(self, memory_path: Path):
        """Test summary generation with real LLM."""
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        from personal_ai.llm import LLMClient
        
        store = MemoryStore(memory_path)
        store.add_message("user", "Test message 1")
        store.add_message("assistant", "Test response 1")

        llm = LLMClient(api_key, "gpt-4o-mini", 0.7)
        store.update_summary(llm, "TestAssistant")

        summary = store.get_summary()
        assert summary is not None
        assert len(summary) > 0

    def test_update_summary_with_no_conversation(self, memory_path: Path):
        """Test that summary update does nothing with empty conversation."""
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping real API test")

        from personal_ai.llm import LLMClient
        
        store = MemoryStore(memory_path)
        llm = LLMClient(api_key, "gpt-4o-mini", 0.7)

        store.update_summary(llm, "TestAssistant")

        # Summary should remain empty since no conversation
        assert store.get_summary() == ""

