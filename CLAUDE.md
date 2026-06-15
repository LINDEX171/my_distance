# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Dependencies are managed with `uv`. The `pyproject.toml` is currently missing — if running `uv sync` fails, you will need to recreate it with `flask>=3.1.3` as a dependency and `requires-python = ">=3.13"`.

```bash
# Install dependencies
uv sync

# Run the development server
uv run flask --app app run

# Run with debug mode
uv run flask --app app run --debug
```

## Architecture

This is a single-file Flask app (`app.py`) that calculates Euclidean distance between two 2D points (x,y).

**Two surfaces share the same business logic:**
- Web UI: `GET /` renders the form, `POST /` computes and re-renders with the result. Points are submitted as comma-separated strings (e.g. `3,4`).
- JSON API: `POST /api/distance` accepts `{"start_point": "x,y", "end_point": "x,y"}` and returns the result. `GET /api/distances` returns all past calculations.

**In-memory state:** The global `distances` list in `app.py` accumulates every calculation for the session. It is not persisted — it resets on every server restart.

**Template:** `templates/index.html` is a minimal Jinja2 template; it receives a `result` dict (or `None`) from `html_calculate()`.

## Known issues in existing code

- `app.py:50` — the `print` statement in `already_calculated()` is after `return` and never executes.
- `app.py:52` — `/api/distance` declares `methods=['POST', 'GET', 'PUT']` but only works correctly with POST (GET/PUT have no JSON body).
- The `result` dict is built twice in `html_calculate()` (once for the response, once for appending to `distances`) — they could share the same object.
