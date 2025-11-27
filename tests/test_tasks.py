"""Tests for TaskManager."""

import json
from pathlib import Path

import pytest

from personal_ai.tasks import Task, TaskManager


class TestTask:
    """Test Task dataclass."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        task = Task(
            id="test-id",
            description="Test task",
            status="open",
            category="work",
            due="2024-12-31T23:59:59",
        )
        data = task.to_dict()
        assert data["id"] == "test-id"
        assert data["description"] == "Test task"
        assert data["status"] == "open"
        assert data["category"] == "work"
        assert data["due"] == "2024-12-31T23:59:59"

    def test_to_dict_without_due(self):
        """Test serialization without due date."""
        task = Task(id="test-id", description="Test task")
        data = task.to_dict()
        assert "due" not in data

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "test-id",
            "description": "Test task",
            "status": "open",
            "category": "work",
            "created_at": "2024-01-01T00:00:00",
        }
        task = Task.from_dict(data)
        assert task.id == "test-id"
        assert task.description == "Test task"
        assert task.status == "open"
        assert task.category == "work"


class TestTaskManager:
    """Test TaskManager persistence and operations."""

    def test_initialization_creates_empty_manager(self, task_path: Path):
        """Test that a new TaskManager starts empty."""
        manager = TaskManager(task_path)
        assert len(manager.list_tasks()) == 0

    def test_add_task(self, task_path: Path):
        """Test adding a task."""
        manager = TaskManager(task_path)
        task = manager.add_task("Buy groceries")

        assert task.description == "Buy groceries"
        assert task.status == "open"
        assert task.category == "general"
        assert len(manager.list_tasks()) == 1

    def test_add_task_with_category(self, task_path: Path):
        """Test adding a task with custom category."""
        manager = TaskManager(task_path)
        task = manager.add_task("Write report", category="work")

        assert task.category == "work"

    def test_persists_tasks(self, task_path: Path):
        """Test that tasks are saved to disk."""
        manager = TaskManager(task_path)
        manager.add_task("Task 1")
        manager.add_task("Task 2")

        # Create a new manager instance to verify persistence
        new_manager = TaskManager(task_path)
        tasks = new_manager.list_tasks()
        assert len(tasks) == 2
        descriptions = [t.description for t in tasks]
        assert "Task 1" in descriptions
        assert "Task 2" in descriptions

    def test_loads_existing_tasks(self, task_path: Path):
        """Test loading existing tasks from file."""
        data = [
            {
                "id": "task-1",
                "description": "Existing task",
                "status": "open",
                "category": "general",
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        task_path.write_text(json.dumps(data))

        manager = TaskManager(task_path)
        tasks = manager.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].description == "Existing task"
        assert tasks[0].id == "task-1"

    def test_list_tasks_with_status_filter(self, task_path: Path):
        """Test filtering tasks by status."""
        manager = TaskManager(task_path)
        task1 = manager.add_task("Open task")
        manager.add_task("Another open task")
        manager.complete_task(task1.id)

        open_tasks = manager.list_tasks(status="open")
        done_tasks = manager.list_tasks(status="done")

        assert len(open_tasks) == 1
        assert len(done_tasks) == 1
        assert done_tasks[0].description == "Open task"

    def test_complete_task(self, task_path: Path):
        """Test marking a task as complete."""
        manager = TaskManager(task_path)
        task = manager.add_task("Task to complete")

        result = manager.complete_task(task.id)
        assert result is True

        completed = manager.get_task(task.id)
        assert completed is not None
        assert completed.status == "done"

    def test_complete_nonexistent_task(self, task_path: Path):
        """Test completing a task that doesn't exist."""
        manager = TaskManager(task_path)
        result = manager.complete_task("nonexistent-id")
        assert result is False

    def test_get_task(self, task_path: Path):
        """Test retrieving a specific task."""
        manager = TaskManager(task_path)
        task = manager.add_task("Test task")

        retrieved = manager.get_task(task.id)
        assert retrieved is not None
        assert retrieved.id == task.id
        assert retrieved.description == "Test task"

    def test_get_nonexistent_task(self, task_path: Path):
        """Test retrieving a task that doesn't exist."""
        manager = TaskManager(task_path)
        task = manager.get_task("nonexistent-id")
        assert task is None

    def test_clear_completed(self, task_path: Path):
        """Test clearing completed tasks."""
        manager = TaskManager(task_path)
        task1 = manager.add_task("Task 1")
        task2 = manager.add_task("Task 2")
        manager.complete_task(task1.id)

        removed_count = manager.clear_completed()
        assert removed_count == 1
        assert len(manager.list_tasks()) == 1
        assert manager.get_task(task1.id) is None
        assert manager.get_task(task2.id) is not None

    def test_handles_corrupted_json(self, task_path: Path):
        """Test graceful handling of corrupted JSON."""
        task_path.write_text("{ invalid json }")
        manager = TaskManager(task_path)
        # Should start with empty state
        assert len(manager.list_tasks()) == 0

