# Python Imports

Always place all import statements at the very top of each Python file, before any code, functions, or classes. Do not put imports inside functions or classes unless absolutely necessary (e.g., to avoid circular imports or for performance reasons in rare cases).
# GitHub Copilot Instructions

## Python Execution

Always run Python scripts using `uv run python` instead of `python`, `python3`, or other Python commands.

Examples:
- ✅ `uv run python script.py`
- ✅ `uv run python -m module`
- ✅ `uv run python -c "print('hello')"`
- ❌ `python script.py`
- ❌ `python3 script.py`

This ensures the correct virtual environment and dependencies are used.

## Project Requirements

Use `TASK_SPEC.md` as the source of truth for the functional requirements of the application.

## Documentation

Do NOT create markdown files to document changes, summaries, or explanations unless explicitly requested by the user. Keep responses concise and in chat.
