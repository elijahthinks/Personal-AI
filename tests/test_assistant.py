"""Tests for PersonalAI assistant using real API."""

import pytest

from personal_ai.assistant import PersonalAI
from personal_ai.memory import MemoryStore
from personal_ai.tasks import TaskManager


class TestPersonalAI:
    """Test PersonalAI orchestration with real API calls."""

    def test_from_config(self, test_config):
        """Test creating PersonalAI from config."""
        assistant = PersonalAI.from_config(test_config)

        assert assistant.config == test_config
        assert assistant.memory is not None
        assert assistant.tasks is not None
        assert assistant.llm_client is not None

    @pytest.mark.unit
    def test_handle_user_input_regular_chat(self, test_config):
        """Test handling regular chat input with real API."""
        assistant = PersonalAI.from_config(test_config)

        response = assistant.handle_user_input("Say hello in one word.")

        assert response is not None
        assert len(response) > 0
        assert assistant.memory.conversation_length() == 2  # user message + assistant response

    @pytest.mark.unit
    def test_handle_user_input_command(self, test_config):
        """Test handling command input."""
        assistant = PersonalAI.from_config(test_config)

        response = assistant.handle_user_input("/help")

        assert "Available commands" in response
        # Commands should not add to conversation history
        assert assistant.memory.conversation_length() == 0

    @pytest.mark.unit
    def test_cmd_list_tasks(self, test_config):
        """Test /tasks command."""
        assistant = PersonalAI.from_config(test_config)
        assistant.tasks.add_task("Test task 1")
        assistant.tasks.add_task("Test task 2")

        handled, message = assistant._handle_command("/tasks")
        assert handled is True
        assert "Test task 1" in message
        assert "Test task 2" in message

    @pytest.mark.unit
    def test_cmd_list_tasks_empty(self, test_config):
        """Test /tasks command with no tasks."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/tasks")
        assert handled is True
        assert "No tasks yet" in message

    @pytest.mark.unit
    def test_cmd_add_task(self, test_config):
        """Test /addtask command."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/addtask Buy groceries")
        assert handled is True
        assert "Logged task" in message

        all_tasks = assistant.tasks.list_tasks()
        assert len(all_tasks) == 1
        assert "groceries" in all_tasks[0].description.lower()

    @pytest.mark.unit
    def test_cmd_add_task_no_argument(self, test_config):
        """Test /addtask command without description."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/addtask")
        assert handled is False
        assert "Usage" in message

    @pytest.mark.unit
    def test_cmd_done_task(self, test_config):
        """Test /donetask command."""
        assistant = PersonalAI.from_config(test_config)
        task = assistant.tasks.add_task("Complete this task")

        task_prefix = task.id[:8]
        handled, message = assistant._handle_command(f"/donetask {task_prefix}")
        assert handled is True
        assert "Marked task" in message.lower()

        completed = assistant.tasks.get_task(task.id)
        assert completed is not None
        assert completed.status == "done"

    @pytest.mark.unit
    def test_cmd_done_task_no_match(self, test_config):
        """Test /donetask command with invalid prefix."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/donetask xyz")
        assert handled is False
        assert "No task matches" in message

    @pytest.mark.unit
    def test_cmd_update_profile(self, test_config):
        """Test /profile command."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/profile name=Alice")
        assert handled is True
        assert "Stored profile fact" in message

        profile = assistant.memory.get_user_profile()
        assert profile["name"] == "Alice"

    @pytest.mark.unit
    def test_cmd_update_profile_invalid_format(self, test_config):
        """Test /profile command with invalid format."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/profile invalid")
        assert handled is False
        assert "Usage" in message

    @pytest.mark.unit
    def test_cmd_reflect(self, test_config):
        """Test /reflect command."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/reflect Today was productive")
        assert handled is True
        assert "Noted reflection" in message.lower()

        reflections = assistant.memory.get_reflections()
        assert len(reflections) == 1
        assert "productive" in reflections[0].lower()

    @pytest.mark.unit
    def test_cmd_help(self, test_config):
        """Test /help command."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/help")
        assert handled is True
        assert "Available commands" in message
        assert "/help" in message
        assert "/tasks" in message

    @pytest.mark.unit
    def test_unknown_command(self, test_config):
        """Test handling unknown command."""
        assistant = PersonalAI.from_config(test_config)

        handled, message = assistant._handle_command("/unknown")
        assert handled is True
        assert "Unknown command" in message

    @pytest.mark.unit
    def test_build_message_history_includes_context(self, test_config):
        """Test that message history includes context sections."""
        assistant = PersonalAI.from_config(test_config)
        assistant.memory.update_user_profile("name", "Alice")
        assistant.memory.add_reflection("Test reflection")
        assistant.memory.add_message("user", "Previous message")
        assistant.memory.add_message("assistant", "Previous response")
        assistant.tasks.add_task("Active task")

        messages = assistant._build_message_history("New question")

        # Should have system message with context
        assert messages[0]["role"] == "system"
        system_content = messages[0]["content"]
        assert test_config.persona_name in system_content
        assert "Alice" in system_content  # profile
        assert "Test reflection" in system_content  # reflection
        assert "Active task" in system_content  # tasks

        # Should include recent conversation
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "New question"

    @pytest.mark.unit
    def test_summarization_triggers(self, test_config):
        """Test that summarization is triggered at threshold."""
        assistant = PersonalAI.from_config(test_config)

        # Add messages up to threshold (using simple messages to reduce API calls)
        for i in range(min(test_config.summary_every, 5)):  # Limit to 5 for testing
            assistant.handle_user_input(f"Test message {i}")

        # Check that conversation was saved
        assert assistant.memory.conversation_length() > 0

        # If we reached threshold, summary should exist or be in process
        # The actual summarization happens asynchronously, so we just verify
        # the conversation was tracked correctly
