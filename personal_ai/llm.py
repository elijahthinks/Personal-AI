"""Wrapper around the OpenAI chat completion API."""

from __future__ import annotations

from typing import Dict, List


class LLMClient:
    """Lightweight OpenAI chat client with graceful degradation."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - requires package
            raise RuntimeError(
                "The 'openai' package is required. Install it with 'pip install openai'."
            ) from exc

        self._client = OpenAI(api_key=api_key)
        self._legacy = None

    def complete_chat(
        self,
        messages: List[Dict[str, str]],
        *,
        max_output_tokens: int = 600,
    ) -> str:
        """Send a chat completion request and return the assistant content."""

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_output_tokens,
            )
            return response.choices[0].message.content.strip()
        except AttributeError:
            return self._complete_chat_legacy(messages, max_output_tokens=max_output_tokens)

    def _complete_chat_legacy(
        self,
        messages: List[Dict[str, str]],
        *,
        max_output_tokens: int,
    ) -> str:
        if self._legacy is None:
            try:
                import openai  # type: ignore[import]
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "OpenAI client not available. Install 'openai>=1.0.0'."
                ) from exc
            openai.api_key = self.api_key
            self._legacy = openai
        completion = self._legacy.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_output_tokens,
        )
        return completion["choices"][0]["message"]["content"].strip()
