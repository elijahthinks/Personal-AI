"""Conversation memory storage."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


Message = Dict[str, str]


@dataclass
class MemoryState:
    conversation: List[Message] = field(default_factory=list)
    summary: str = ""
    user_profile: Dict[str, str] = field(default_factory=dict)
    reflections: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "conversation": self.conversation,
            "summary": self.summary,
            "user_profile": self.user_profile,
            "reflections": self.reflections,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "MemoryState":
        return cls(
            conversation=list(data.get("conversation", [])),
            summary=str(data.get("summary", "")),
            user_profile=dict(data.get("user_profile", {})),
            reflections=list(data.get("reflections", [])),
        )


class MemoryStore:
    """Simple persistent memory built on a JSON file."""

    def __init__(self, path: Path):
        self.path = path
        self.state = MemoryState()
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            data = {}
        self.state = MemoryState.from_dict(data)

    def save(self) -> None:
        self.path.write_text(json.dumps(self.state.to_dict(), indent=2))

    def add_message(self, role: str, content: str) -> None:
        self.state.conversation.append({"role": role, "content": content})
        self.save()

    def get_recent(self, limit: int) -> List[Message]:
        if limit <= 0:
            return self.state.conversation
        return self.state.conversation[-limit:]

    def conversation_length(self) -> int:
        return len(self.state.conversation)

    def should_summarize(self, threshold: int) -> bool:
        return threshold > 0 and self.conversation_length() >= threshold

    def update_summary(
        self,
        llm_client: "LLMClient",
        persona_name: str,
        max_tokens: int = 400,
    ) -> None:
        """Generate or refresh the long-term summary."""

        if not self.state.conversation:
            return

        prompt = [
            {
                "role": "system",
                "content": (
                    "You are updating the long-term memory summary for a personal AI assistant. "
                    "Capture key user details, preferences, goals, and emotional notes. "
                    "Write in bullet points."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(self.state.conversation[-20:], ensure_ascii=False),
            },
        ]

        summary = llm_client.complete_chat(prompt, max_output_tokens=max_tokens)
        self.state.summary = summary.strip()
        self.save()

    def get_summary(self) -> str:
        return self.state.summary

    def add_reflection(self, note: str) -> None:
        self.state.reflections.append(note)
        self.save()

    def get_reflections(self) -> List[str]:
        return self.state.reflections

    def update_user_profile(self, key: str, value: str) -> None:
        self.state.user_profile[key] = value
        self.save()

    def get_user_profile(self) -> Dict[str, str]:
        return dict(self.state.user_profile)
