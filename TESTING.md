# Testing Guide

This document describes how to test the Personal AI platform.

## Setup

1. Install testing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure you have pytest installed:
   ```bash
   pip install pytest pytest-mock pytest-cov
   ```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=personal_ai --cov-report=term-missing
```

### Run specific test files
```bash
pytest tests/test_memory.py
pytest tests/test_tasks.py
pytest tests/test_assistant.py
```

### Run specific test markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with verbose output
```bash
pytest -v
```

### Run a specific test
```bash
pytest tests/test_memory.py::TestMemoryStore::test_persists_messages
```

## Test Structure

- **Unit Tests**: Test individual components in isolation
  - `test_memory.py` - MemoryStore persistence and operations
  - `test_tasks.py` - TaskManager functionality
  - `test_llm.py` - LLMClient with mocked OpenAI API
  - `test_assistant.py` - PersonalAI command handling
  - `test_config.py` - Configuration loading
  - `test_cli.py` - CLI interface

- **Integration Tests**: Test full workflows
  - `tests/integration/test_full_flow.py` - End-to-end scenarios

## Writing New Tests

1. Place unit tests in `tests/test_*.py`
2. Place integration tests in `tests/integration/`
3. Use fixtures from `tests/conftest.py` for common setup
4. Mock external dependencies (like OpenAI API) using `pytest-mock`
5. Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`

## Example Test

```python
import pytest
from personal_ai.memory import MemoryStore

def test_add_message(memory_path):
    """Test adding a message to memory."""
    store = MemoryStore(memory_path)
    store.add_message("user", "Hello")
    assert store.conversation_length() == 1
```

## Test Coverage

View HTML coverage report:
```bash
pytest --cov=personal_ai --cov-report=html
open htmlcov/index.html
```

