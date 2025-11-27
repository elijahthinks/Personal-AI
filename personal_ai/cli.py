"""Command line interaction loop for the personal AI assistant."""

from __future__ import annotations

from dataclasses import dataclass

from .assistant import PersonalAI
from .config import PersonalAIConfig, load_config

try:
    from rich.console import Console
    from rich.markdown import Markdown
except ImportError:  # pragma: no cover
    Console = None
    Markdown = None


@dataclass
class PersonalAIConsoleApp:
    config: PersonalAIConfig
    assistant: PersonalAI

    @classmethod
    def from_env(cls) -> "PersonalAIConsoleApp":
        config = load_config()
        assistant = PersonalAI.from_config(config)
        return cls(config=config, assistant=assistant)

    def run(self) -> None:
        console = Console() if Console else None
        greet = f"Connected to {self.config.persona_name}. Type /help for commands. Ctrl+C to exit."
        if console:
            console.print(f"[bold cyan]{greet}[/bold cyan]")
        else:
            print(greet)

        try:
            while True:
                if console:
                    user_input = console.input("[green]You[/green]: ").strip()
                else:
                    user_input = input("You: ").strip()
                if not user_input:
                    continue

                response = self.assistant.handle_user_input(user_input)
                self._display_response(response, console)
        except (KeyboardInterrupt, EOFError):
            message = "Goodbye. Keep making progress!"
            if console:
                console.print(f"\n[bold yellow]{message}[/bold yellow]")
            else:
                print("\n" + message)

    def _display_response(self, response: str, console: Console | None) -> None:
        if not console or not Markdown:
            print(f"{self.config.persona_name}: {response}")
            return
        console.print()
        console.print(Markdown(response))
        console.print()
