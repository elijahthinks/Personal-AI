"""Entry point for the personal AI console experience."""

from personal_ai.cli import PersonalAIConsoleApp


def main() -> None:
    app = PersonalAIConsoleApp.from_env()
    app.run()


if __name__ == "__main__":
    main()
