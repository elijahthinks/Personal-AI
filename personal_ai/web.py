"""Web server for Personal AI platform."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from .assistant import PersonalAI
from .config import PersonalAIConfig, load_config
from .memory import MemoryStore
from .tasks import Task, TaskManager


def create_app(config: PersonalAIConfig | None = None) -> Flask:
    """Create and configure Flask application."""
    from pathlib import Path
    template_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    app = Flask(__name__, template_folder=str(template_dir), static_folder=str(static_dir))
    CORS(app)

    # Load config if not provided
    if config is None:
        try:
            config = load_config()
        except RuntimeError as e:
            app.logger.error(f"Configuration error: {e}")
            raise

    # Initialize assistant
    assistant = PersonalAI.from_config(config)

    @app.route("/")
    def index():
        """Serve the main UI page."""
        return render_template("index.html", persona_name=config.persona_name)

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Handle chat messages and commands."""
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "Message cannot be empty"}), 400

        try:
            response = assistant.handle_user_input(user_input)
            return jsonify({"response": response})
        except Exception as e:
            app.logger.error(f"Error processing message: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/conversation", methods=["GET"])
    def get_conversation():
        """Get conversation history."""
        try:
            messages = assistant.memory.get_recent(100)
            return jsonify({"messages": messages})
        except Exception as e:
            app.logger.error(f"Error getting conversation: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/tasks", methods=["GET"])
    def get_tasks():
        """Get all tasks."""
        try:
            status = request.args.get("status")
            tasks = assistant.tasks.list_tasks(status=status)
            return jsonify({
                "tasks": [
                    {
                        "id": task.id,
                        "description": task.description,
                        "status": task.status,
                        "category": task.category,
                        "created_at": task.created_at,
                        "due": task.due,
                    }
                    for task in tasks
                ]
            })
        except Exception as e:
            app.logger.error(f"Error getting tasks: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/tasks", methods=["POST"])
    def add_task():
        """Add a new task."""
        data = request.get_json()
        description = data.get("description", "").strip()
        category = data.get("category", "general")
        due = data.get("due")

        if not description:
            return jsonify({"error": "Task description cannot be empty"}), 400

        try:
            task = assistant.tasks.add_task(description, category=category, due=due)
            return jsonify({
                "task": {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status,
                    "category": task.category,
                    "created_at": task.created_at,
                    "due": task.due,
                }
            }), 201
        except Exception as e:
            app.logger.error(f"Error adding task: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/tasks/<task_id>", methods=["PUT"])
    def update_task(task_id: str):
        """Update a task (mark as done, etc.)."""
        data = request.get_json()
        status = data.get("status")

        if status == "done":
            try:
                result = assistant.tasks.complete_task(task_id)
                if result:
                    return jsonify({"success": True})
                else:
                    return jsonify({"error": "Task not found"}), 404
            except Exception as e:
                app.logger.error(f"Error updating task: {e}")
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Only status 'done' is supported"}), 400

    @app.route("/api/profile", methods=["GET"])
    def get_profile():
        """Get user profile."""
        try:
            profile = assistant.memory.get_user_profile()
            return jsonify({"profile": profile})
        except Exception as e:
            app.logger.error(f"Error getting profile: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/profile", methods=["POST"])
    def update_profile():
        """Update user profile."""
        data = request.get_json()
        key = data.get("key", "").strip()
        value = data.get("value", "").strip()

        if not key or not value:
            return jsonify({"error": "Key and value are required"}), 400

        try:
            assistant.memory.update_user_profile(key, value)
            return jsonify({"success": True})
        except Exception as e:
            app.logger.error(f"Error updating profile: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/reflections", methods=["GET"])
    def get_reflections():
        """Get reflections."""
        try:
            reflections = assistant.memory.get_reflections()
            return jsonify({"reflections": reflections})
        except Exception as e:
            app.logger.error(f"Error getting reflections: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/reflections", methods=["POST"])
    def add_reflection():
        """Add a reflection."""
        data = request.get_json()
        note = data.get("note", "").strip()

        if not note:
            return jsonify({"error": "Reflection note cannot be empty"}), 400

        try:
            assistant.memory.add_reflection(note)
            return jsonify({"success": True}), 201
        except Exception as e:
            app.logger.error(f"Error adding reflection: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/summary", methods=["GET"])
    def get_summary():
        """Get long-term summary."""
        try:
            summary = assistant.memory.get_summary()
            return jsonify({"summary": summary})
        except Exception as e:
            app.logger.error(f"Error getting summary: {e}")
            return jsonify({"error": str(e)}), 500

    return app


def run_web_server(host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
    """Run the web server."""
    try:
        config = load_config()
    except RuntimeError as e:
        print(f"Error loading configuration: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment.")
        return

    app = create_app(config)
    print(f"Starting Personal AI web server at http://{host}:{port}")
    print(f"Connected to {config.persona_name}")
    app.run(host=host, port=port, debug=debug)

