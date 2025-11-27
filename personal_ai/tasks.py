"""Task and goal management for the personal AI."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


@dataclass
class Task:
    id: str
    description: str
    status: str = "open"
    category: str = "general"
    created_at: str = field(default_factory=lambda: datetime.utcnow().strftime(ISO_FORMAT))
    due: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        data: Dict[str, str] = {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "category": self.category,
            "created_at": self.created_at,
        }
        if self.due:
            data["due"] = self.due
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Task":
        return cls(
            id=data["id"],
            description=data["description"],
            status=data.get("status", "open"),
            category=data.get("category", "general"),
            created_at=data.get("created_at", datetime.utcnow().strftime(ISO_FORMAT)),
            due=data.get("due"),
        )


class TaskManager:
    """Simple persistent task list."""

    def __init__(self, path: Path):
        self.path = path
        self._tasks: Dict[str, Task] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            items = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            items = []
        for item in items:
            task = Task.from_dict(item)
            self._tasks[task.id] = task

    def save(self) -> None:
        payload = [task.to_dict() for task in self._tasks.values()]
        self.path.write_text(json.dumps(payload, indent=2))

    def add_task(self, description: str, *, category: str = "general", due: Optional[str] = None) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, description=description, category=category, due=due)
        self._tasks[task_id] = task
        self.save()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        tasks = list(self._tasks.values())
        if status is None:
            return tasks
        return [task for task in tasks if task.status == status]

    def complete_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = "done"
        self.save()
        return True

    def clear_completed(self) -> int:
        done_ids = [task_id for task_id, task in self._tasks.items() if task.status == "done"]
        for task_id in done_ids:
            self._tasks.pop(task_id, None)
        self.save()
        return len(done_ids)

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)
