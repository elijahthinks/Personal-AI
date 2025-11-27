"""Tests for configuration loading."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from personal_ai.config import PersonalAIConfig, load_config


class TestPersonalAIConfig:
    """Test PersonalAIConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = PersonalAIConfig(api_key="test-key")
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.persona_name == "Jarvis"
        assert config.max_context_messages == 12
        assert config.summary_every == 16

    def test_custom_values(self):
        """Test custom configuration values."""
        config = PersonalAIConfig(
            api_key="test-key",
            model="gpt-4",
            temperature=0.9,
            persona_name="CustomBot",
            max_context_messages=20,
            summary_every=30,
        )
        assert config.model == "gpt-4"
        assert config.temperature == 0.9
        assert config.persona_name == "CustomBot"
        assert config.max_context_messages == 20
        assert config.summary_every == 30

    def test_ensure_storage(self, temp_dir: Path):
        """Test that ensure_storage creates directories."""
        memory_path = temp_dir / "memory" / "state.json"
        task_path = temp_dir / "tasks" / "tasks.json"

        config = PersonalAIConfig(
            api_key="test-key", memory_path=memory_path, task_path=task_path
        )
        config.ensure_storage()

        assert memory_path.parent.exists()
        assert task_path.parent.exists()


class TestLoadConfig:
    """Test load_config function."""

    def test_loads_from_environment(self, monkeypatch):
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key-123")
        monkeypatch.setenv("PERSONAL_AI_MODEL", "gpt-4")
        monkeypatch.setenv("PERSONAL_AI_TEMPERATURE", "0.9")
        monkeypatch.setenv("PERSONAL_AI_PERSONA_NAME", "TestBot")

        config = load_config()

        assert config.api_key == "env-key-123"
        assert config.model == "gpt-4"
        assert config.temperature == 0.9
        assert config.persona_name == "TestBot"

    def test_missing_api_key_raises_error(self, monkeypatch):
        """Test that missing API key raises RuntimeError."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(RuntimeError, match="Missing OPENAI_API_KEY"):
            load_config()

    def test_loads_custom_paths(self, monkeypatch, temp_dir: Path):
        """Test loading custom storage paths."""
        memory_path = temp_dir / "custom_memory.json"
        task_path = temp_dir / "custom_tasks.json"

        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("PERSONAL_AI_STATE_PATH", str(memory_path))
        monkeypatch.setenv("PERSONAL_AI_TASK_PATH", str(task_path))

        config = load_config()

        assert config.memory_path == memory_path.expanduser()
        assert config.task_path == task_path.expanduser()

    def test_uses_default_paths_when_not_set(self, monkeypatch):
        """Test that default paths are used when env vars not set."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("PERSONAL_AI_STATE_PATH", raising=False)
        monkeypatch.delenv("PERSONAL_AI_TASK_PATH", raising=False)

        config = load_config()

        assert config.memory_path == Path.home() / ".personal_ai" / "state.json"
        assert config.task_path == Path.home() / ".personal_ai" / "tasks.json"

    def test_uses_api_key_parameter(self, monkeypatch):
        """Test that explicit api_key parameter overrides env."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")

        config = load_config(api_key="param-key")

        assert config.api_key == "param-key"

    @patch("personal_ai.config.load_dotenv")
    def test_loads_dotenv(self, mock_load_dotenv, monkeypatch):
        """Test that .env file is loaded."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        # Reset the global flag
        import personal_ai.config as config_module

        config_module._DOTENV_LOADED = False

        load_config()

        # Should attempt to load .env file
        mock_load_dotenv.assert_called_once()

