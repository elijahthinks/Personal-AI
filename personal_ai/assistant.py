"""Core orchestration for the personal AI assistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .config import PersonalAIConfig
from .llm import LLMClient
from .memory import MemoryStore
from .tasks import TaskManager


CommandResult = Tuple[bool, str]


@dataclass
class PersonalAI:
    """High-level interface bundling LLM, memory, and task management."""

    config: PersonalAIConfig
    llm_client: LLMClient
    memory: MemoryStore
    tasks: TaskManager

    @classmethod
    def from_config(cls, config: PersonalAIConfig) -> "PersonalAI":
        memory_store = MemoryStore(config.memory_path)
        task_manager = TaskManager(config.task_path)
        client = LLMClient(config.api_key, config.model, config.temperature)
        return cls(config=config, llm_client=client, memory=memory_store, tasks=task_manager)

    def handle_user_input(self, user_input: str) -> str:
        if user_input.startswith("/"):
            _, message = self._handle_command(user_input)
            return message
        return self._chat(user_input)

    def _chat(self, user_input: str) -> str:
        messages = self._build_message_history(user_input)
        reply = self.llm_client.complete_chat(messages)
        self.memory.add_message("user", user_input)
        self.memory.add_message("assistant", reply)
        if self.memory.should_summarize(self.config.summary_every):
            self.memory.update_summary(self.llm_client, self.config.persona_name)
        return reply

    def _build_message_history(self, user_input: str):
        summary = self.memory.get_summary()
        reflections = self.memory.get_reflections()
        profile = self.memory.get_user_profile()
        open_tasks = self.tasks.list_tasks(status="open")

        context_sections = []
        if summary:
            context_sections.append(f"Long-term summary:\n{summary}")
        if reflections:
            context_sections.append("Recent reflections:\n" + "\n".join(f"- {note}" for note in reflections[-5:]))
        if profile:
            profile_lines = "\n".join(f"- {key}: {value}" for key, value in profile.items())
            context_sections.append(f"Known user profile facts:\n{profile_lines}")
        if open_tasks:
            lines = "\n".join(f"- {task.description} (id {task.id[:8]})" for task in open_tasks[:6])
            context_sections.append("Active goals and tasks:\n" + lines)

        system_parts = [
            f"You are {self.config.persona_name}, a proactive and empathetic personal AI companion.",
            self.config.persona_description,
            "Always give thoughtful, specific guidance while respecting user autonomy.",
        ]
        if context_sections:
            system_parts.append("\n".join(context_sections))

        system_message = {"role": "system", "content": "\n\n".join(system_parts)}
        history = self.memory.get_recent(self.config.max_context_messages)
        history = history[-self.config.max_context_messages :]

        messages = [system_message]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        return messages

    def _handle_command(self, raw: str) -> CommandResult:
        tokens = raw[1:].strip().split(" ", 1)
        command = tokens[0].lower()
        argument = tokens[1].strip() if len(tokens) > 1 else ""

        handlers = {
            "tasks": self._cmd_list_tasks,
            "addtask": self._cmd_add_task,
            "donetask": self._cmd_done_task,
            "profile": self._cmd_update_profile,
            "reflect": self._cmd_reflect,
            "help": self._cmd_help,
        }

        handler = handlers.get(command)
        if not handler:
            return True, f"Unknown command '{command}'. Type /help for options."
        return handler(argument)

    def _cmd_list_tasks(self, _: str) -> CommandResult:
        tasks = self.tasks.list_tasks()
        if not tasks:
            return True, "No tasks yet. Add one with /addtask <description>"
        lines = [f"{task.id[:8]} | {task.status:<6} | {task.description} ({task.category})" for task in tasks]
        return True, "\n".join(lines)

    def _cmd_add_task(self, argument: str) -> CommandResult:
        if not argument:
            return False, "Usage: /addtask <description>"
        task = self.tasks.add_task(argument)
        return True, f"Logged task {task.id[:8]}."

    def _cmd_done_task(self, argument: str) -> CommandResult:
        if not argument:
            return False, "Usage: /donetask <task_id_prefix>"
        candidates = [task for task in self.tasks.list_tasks() if task.id.startswith(argument)]
        if not candidates:
            return False, f"No task matches prefix '{argument}'."
        task = candidates[0]
        self.tasks.complete_task(task.id)
        return True, f"Marked task {task.id[:8]} as done."

    def _cmd_update_profile(self, argument: str) -> CommandResult:
        if "=" not in argument:
            return False, "Usage: /profile key=value"
        key, value = [part.strip() for part in argument.split("=", 1)]
        if not key or not value:
            return False, "Usage: /profile key=value"
        self.memory.update_user_profile(key, value)
        return True, f"Stored profile fact '{key}'."

    def _cmd_reflect(self, argument: str) -> CommandResult:
        if not argument:
            return False, "Usage: /reflect <note>"
        self.memory.add_reflection(argument)
        return True, "Noted reflection."

    def _cmd_help(self, _: str) -> CommandResult:
        lines = [
            "Available commands:",
            "/help                Show this message",
            "/tasks               List tasks and goals",
            "/addtask <desc>      Capture a new task",
            "/donetask <prefix>   Mark a task complete",
            "/profile k=v         Store a profile fact",
            "/reflect <note>      Save a reflection or lesson",
        ]
        return True, "\n".join(lines)
