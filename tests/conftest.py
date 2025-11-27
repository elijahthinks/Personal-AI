"""Shared fixtures and test utilities."""

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from personal_ai.config import PersonalAIConfig


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def memory_path(temp_dir: Path) -> Path:
    """Path to a temporary memory file."""
    return temp_dir / "test_state.json"


@pytest.fixture
def task_path(temp_dir: Path) -> Path:
    """Path to a temporary task file."""
    return temp_dir / "test_tasks.json"


@pytest.fixture
def test_config(memory_path: Path, task_path: Path, monkeypatch) -> PersonalAIConfig:
    """Create a test configuration with temporary paths and a real API key from environment."""
    import os
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping tests that require real API")
    
    config = PersonalAIConfig(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.7,
        memory_path=memory_path,
        task_path=task_path,
        persona_name="TestAssistant",
        persona_description="A test assistant.",
        max_context_messages=12,
        summary_every=16,
    )
    config.ensure_storage()
    return config

