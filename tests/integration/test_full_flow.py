"""Integration tests for full platform workflows using real API."""

import pytest

from personal_ai.assistant import PersonalAI


@pytest.mark.integration
class TestFullWorkflow:
    """End-to-end integration tests with real API."""

    def test_task_workflow(self, test_config):
        """Test complete task management workflow."""
        assistant = PersonalAI.from_config(test_config)

        # Add a task
        response = assistant.handle_user_input("/addtask Complete integration tests")
        assert "Logged task" in response

        # List tasks
        response = assistant.handle_user_input("/tasks")
        assert "Complete integration tests" in response

        # Get task ID from response or list
        tasks = assistant.tasks.list_tasks()
        task_id_prefix = tasks[0].id[:8]

        # Complete task
        response = assistant.handle_user_input(f"/donetask {task_id_prefix}")
        assert "Marked task" in response.lower()

        # Verify task is done
        completed = assistant.tasks.get_task(tasks[0].id)
        assert completed.status == "done"

    def test_profile_and_memory_workflow(self, test_config):
        """Test profile and reflection workflow."""
        assistant = PersonalAI.from_config(test_config)

        # Update profile
        response = assistant.handle_user_input("/profile name=Alice")
        assert "Stored profile fact" in response

        # Add reflection
        response = assistant.handle_user_input("/reflect Working on AI project")
        assert "Noted reflection" in response.lower()

        # Verify persistence
        profile = assistant.memory.get_user_profile()
        assert profile["name"] == "Alice"

        reflections = assistant.memory.get_reflections()
        assert len(reflections) == 1
        assert "AI project" in reflections[0]

    def test_conversation_context_workflow(self, test_config):
        """Test that conversation context is maintained with real API."""
        assistant = PersonalAI.from_config(test_config)

        # First message
        response1 = assistant.handle_user_input("My name is Bob. Remember this.")
        assert response1 is not None
        assert len(response1) > 0

        # Second message should have context
        response2 = assistant.handle_user_input("What is my name?")
        assert response2 is not None
        # The AI should remember the name from context (though exact response varies)
        assert len(response2) > 0

        # Verify messages are stored
        assert assistant.memory.conversation_length() == 4  # 2 user + 2 assistant

        # Verify context building includes previous conversation
        messages = assistant._build_message_history("Test")
        assert len(messages) > 1  # system + history + current
