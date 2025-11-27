"""Configuration helpers for the personal AI assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_DOTENV_LOADED = False

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


def _ensure_dotenv_loaded() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED or load_dotenv is None:
        _DOTENV_LOADED = True
        return
    load_dotenv()
    _DOTENV_LOADED = True


@dataclass
class PersonalAIConfig:
    """Runtime configuration for the personal AI system."""

    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    memory_path: Path = Path.home() / ".personal_ai" / "state.json"
    task_path: Path = Path.home() / ".personal_ai" / "tasks.json"
    persona_name: str = "Jarvis"
    persona_description: str = (
        "You are a loyal, proactive personal AI companion focused on helping the user learn, "
        "grow, and stay aligned with their goals. Speak with warmth, curiosity, and humility."
    )
    max_context_messages: int = 12
    summary_every: int = 16

    def ensure_storage(self) -> None:
        """Create parent directories for storage."""
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.task_path.parent.mkdir(parents=True, exist_ok=True)


def load_config(
    *, api_key: Optional[str] = None, config_path: Optional[Path] = None
) -> PersonalAIConfig:
    """Load configuration from env variables and optional config file."""

    _ensure_dotenv_loaded()

    env = os.environ
    key = api_key or env.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Set it as an environment variable or pass api_key explicitly."
        )

    model = env.get("PERSONAL_AI_MODEL", "gpt-4o-mini").strip()
    temp = float(env.get("PERSONAL_AI_TEMPERATURE", "0.7"))

    memory_path = env.get("PERSONAL_AI_STATE_PATH")
    if memory_path:
        memory = Path(memory_path).expanduser()
    else:
        memory = Path.home() / ".personal_ai" / "state.json"

    task_path = env.get("PERSONAL_AI_TASK_PATH")
    if task_path:
        tasks_file = Path(task_path).expanduser()
    else:
        tasks_file = memory.with_name("tasks.json")

    persona_name = env.get("PERSONAL_AI_PERSONA_NAME", "Jarvis").strip()
    persona_description = env.get(
        "PERSONAL_AI_PERSONA_DESCRIPTION",
        "You are a loyal, proactive personal AI companion focused on helping the user learn, "
        "grow, and stay aligned with their goals. Speak with warmth, curiosity, and humility.",
    ).strip()

    max_context = int(env.get("PERSONAL_AI_MAX_CONTEXT_MESSAGES", "12"))
    summary_every = int(env.get("PERSONAL_AI_SUMMARY_EVERY", "16"))

    cfg = PersonalAIConfig(
        api_key=key,
        model=model,
        temperature=temp,
        memory_path=memory,
        persona_name=persona_name,
        task_path=tasks_file,
        persona_description=persona_description,
        max_context_messages=max_context,
        summary_every=summary_every,
    )
    cfg.ensure_storage()
    return cfg
