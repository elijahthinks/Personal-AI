# Personal AI Prototype

A Python console companion inspired by the Jarvis vision: natural conversation, gentle coaching, and proactive help grounded in your goals.

## Features
- Conversational assistant powered by OpenAI chat models with configurable persona.
- Persistent memory that captures conversation context, profile facts, and reflections.
- Basic goal and task tracker with `/addtask`, `/tasks`, and `/donetask` commands.
- Long-term summary refresh to keep responses aligned with your history.
- Markdown-friendly console output (via `rich`) for readable replies.

## Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Expose your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   Optionally, create a `.env` file with the same key; the app loads it automatically.

## Running

### Web UI (Recommended)

Launch the web interface:

```bash
python web.py
```

Or with custom port:
```bash
python web.py 8080
```

Then open your browser to `http://127.0.0.1:5000` (or your custom port).

The web UI provides:
- Real-time chat interface
- Task management sidebar
- Profile information panel
- Reflections tracker
- Beautiful dark theme

### Console Interface

For command-line usage:

```bash
python main.py
```

Interact naturally or use slash commands for structure:
- `/help` – show command list
- `/addtask <description>` – log a new task
- `/tasks` – list tasks
- `/donetask <idprefix>` – mark complete
- `/profile key=value` – store personal facts
- `/reflect <note>` – capture insights

State is stored under `~/.personal_ai/` by default. Customize behavior with environment variables:
- `PERSONAL_AI_MODEL` – model name (default `gpt-4o-mini`)
- `PERSONAL_AI_TEMPERATURE` – creativity level
- `PERSONAL_AI_STATE_PATH` / `PERSONAL_AI_TASK_PATH` – storage locations
- `PERSONAL_AI_PERSONA_NAME` / `PERSONAL_AI_PERSONA_DESCRIPTION` – voice and tone

## Next Ideas
- Hook in calendar/email APIs for real task automation.
- Add voice input/output for a hands-free experience.
- Expand memory with semantic search and richer reflections.
