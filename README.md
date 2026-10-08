# Personal AI

A "Jarvis"-style personal AI companion written in Python. You can chat with it in the terminal or a web browser. It remembers your conversations, your goals and tasks, and facts about you, and uses that context to give more personal, helpful replies.

> **📚 About this project**
>
> This is a personal learning project. I'm building it to learn how to work with LLM APIs, write Python apps with Flask, store data, and write tests. It's a work in progress with rough edges, not production software. Feedback and suggestions are welcome!

## What it does

- **Chat with memory** – conversations are saved, so the assistant has context from earlier chats.
- **Long-term summary** – the assistant periodically summarizes your history to stay aligned with your goals.
- **Tasks and goals** – add, list, and complete tasks; open tasks are shared with the assistant.
- **Profile facts and reflections** – store things about yourself and notes or lessons you want it to remember.
- **Two ways to use it** – a web UI (chat plus sidebars for tasks, profile, and reflections) or a console app.
- **Configurable persona** – change the assistant's name and personality.

## How it works

```
personal_ai/
├── config.py      # Loads settings from environment variables / .env
├── llm.py         # Small wrapper around the OpenAI chat API
├── memory.py      # Saves conversation, summary, profile, reflections (JSON file)
├── tasks.py       # Saves the task list (JSON file)
├── assistant.py   # Builds the prompt with your context and handles /commands
├── cli.py         # Console chat loop (uses `rich`)
├── web.py         # Flask web server and REST API
├── templates/     # Web UI page
└── static/        # Web UI CSS and JavaScript
main.py            # Starts the console app
web.py             # Starts the web app
tests/             # pytest test suite
```

Everything is stored locally in `~/.personal_ai/` (`state.json` and `tasks.json`).

## Getting started

You need Python 3.10+ and an OpenAI API key.

1. Clone the repo and create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your OpenAI API key, either as an environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
   or by copying `.env.example` to `.env` and filling in the key.

### Run the web UI

```bash
python web.py          # http://127.0.0.1:5000
python web.py 8080     # custom port
python web.py --debug  # Flask debug mode
```

### Run the console app

```bash
python main.py
```

## Commands

Type these in either the console or the web chat:

| Command | What it does |
|---|---|
| `/help` | Show the command list |
| `/addtask <description>` | Add a new task |
| `/tasks` | List your tasks |
| `/donetask <id prefix>` | Mark a task as done |
| `/profile key=value` | Save a fact about yourself |
| `/reflect <note>` | Save a reflection or lesson |

Anything else is sent to the assistant as a normal chat message.

## Configuration

Optional environment variables (or `.env` entries):

| Variable | Default | Purpose |
|---|---|---|
| `PERSONAL_AI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `PERSONAL_AI_TEMPERATURE` | `0.7` | Creativity of replies |
| `PERSONAL_AI_PERSONA_NAME` | `Jarvis` | Assistant's name |
| `PERSONAL_AI_PERSONA_DESCRIPTION` | (built-in) | Assistant's personality and tone |
| `PERSONAL_AI_STATE_PATH` | `~/.personal_ai/state.json` | Where memory is saved |
| `PERSONAL_AI_TASK_PATH` | next to the state file | Where tasks are saved |
| `PERSONAL_AI_MAX_CONTEXT_MESSAGES` | `12` | Recent messages sent with each chat |
| `PERSONAL_AI_SUMMARY_EVERY` | `16` | Message count before summaries start |

## Testing

```bash
pytest
```

The tests mock the OpenAI client, so you don't need an API key to run them. See [TESTING.md](TESTING.md) for more options.

## What I'm learning and what's next

Things I want to explore as I keep building:

- Fix known issues, such as summaries running on every message once the history passes 16 messages, and conversation history that grows without limit.
- Add tests for the web server.
- Semantic search over memory.
- Calendar and email integrations for real task automation.
- Voice input and output for hands-free use.
