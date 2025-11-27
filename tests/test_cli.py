"""Tests for CLI interface."""

import pytest
from unittest.mock import patch

from personal_ai.cli import PersonalAIConsoleApp
from personal_ai.config import PersonalAIConfig


class TestPersonalAIConsoleApp:
    """Test CLI console app."""

    def test_from_env(self, test_config, mocker):
        """Test creating app from environment."""
        mocker.patch("personal_ai.cli.load_config", return_value=test_config)
        mocker.patch("personal_ai.cli.PersonalAI.from_config")

        app = PersonalAIConsoleApp.from_env()

        assert app.config == test_config

    @pytest.mark.unit
    def test_display_response_with_rich(self, test_config):
        """Test response display with rich library available."""
        from unittest.mock import Mock
        from personal_ai.assistant import PersonalAI
        mock_console = Mock()

        with patch("personal_ai.cli.Console", return_value=mock_console):
            with patch("personal_ai.cli.Markdown"):
                assistant = PersonalAI.from_config(test_config)
                app = PersonalAIConsoleApp(config=test_config, assistant=assistant)
                app._display_response("# Response\nTest", mock_console)

                mock_console.print.assert_called()

    @pytest.mark.unit
    def test_display_response_without_rich(self, test_config):
        """Test response display fallback when rich is not available."""
        from personal_ai.assistant import PersonalAI
        assistant = PersonalAI.from_config(test_config)
        app = PersonalAIConsoleApp(config=test_config, assistant=assistant)

        # Mock Console as None to simulate missing rich
        app._display_response("Test response", None)

        # Should not crash - this is a no-op when console is None

    @pytest.mark.integration
    def test_run_with_keyboard_interrupt(self, test_config):
        """Test that KeyboardInterrupt is handled gracefully."""
        from unittest.mock import Mock
        from personal_ai.assistant import PersonalAI
        mock_console = Mock()
        mock_console.input.side_effect = KeyboardInterrupt()

        assistant = PersonalAI.from_config(test_config)
        app = PersonalAIConsoleApp(config=test_config, assistant=assistant)

        with patch("personal_ai.cli.Console", return_value=mock_console):
            # Should not raise, but handle gracefully
            try:
                app.run()
            except KeyboardInterrupt:
                pass  # Expected

        # Should have shown goodbye message
        mock_console.print.assert_called()

    @pytest.mark.integration
    def test_run_handles_empty_input(self, test_config):
        """Test that empty input is handled."""
        from unittest.mock import Mock
        from personal_ai.assistant import PersonalAI
        mock_console = Mock()
        mock_console.input.side_effect = ["", "test message", KeyboardInterrupt()]

        assistant = PersonalAI.from_config(test_config)
        assistant.handle_user_input = Mock(return_value="Response")

        app = PersonalAIConsoleApp(config=test_config, assistant=assistant)

        with patch("personal_ai.cli.Console", return_value=mock_console):
            try:
                app.run()
            except KeyboardInterrupt:
                pass

        # Should have called handle_user_input for non-empty input
        assert assistant.handle_user_input.call_count == 1
        assistant.handle_user_input.assert_called_with("test message")
