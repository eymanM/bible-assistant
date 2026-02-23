# Repository Guidelines

## Project Structure & Module Organization
`app.py` is the Flask entrypoint and defines the public API (`/search`, `/health`) plus request/auth validation.  
`search_service.py` handles retrieval orchestration, translation flow, and SSE streaming (`results`, `token`, `end`).  
`utils.py`, `bible_lookup.py`, and `constants.py` contain shared helpers, Bible formatting/lookup logic, and static config.  
`data/` stores source assets and vector DB artifacts (`data/db`, `data/commentary_db`) plus scripts such as `data/create_db.py`.  
`tests/` contains pytest tests, with shared mocks/fixtures in `tests/conftest.py`.

## Build, Test, and Development Commands
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Use `python app.py` for local development (Flask server on `127.0.0.1:5000`).

```bash
python serve.py
```
Runs a production-style server via Waitress.

```bash
python -m pytest tests -q
```
Runs the full test suite. Use targeted runs for faster iteration, e.g. `python -m pytest tests/test_search.py -q`.

## Coding Style & Naming Conventions
Target Python 3.12 and follow PEP 8 with 4-space indentation.  
Use `snake_case` for functions/variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants.  
Keep route handlers thin in `app.py`; place core logic in `search_service.py`/`utils.py`.  
Preserve SSE response structure and event names to avoid breaking clients.

## Testing Guidelines
Testing uses `pytest` with `unittest.mock` (`MagicMock`, `patch`) to isolate external services (LLMs, Chroma, DB).  
Name files `tests/test_*.py` and tests `test_*`.  
Add regression tests for input validation and streaming behavior when changing search logic.  
Prefer fixture reuse from `tests/conftest.py` over per-test setup duplication.

## Commit & Pull Request Guidelines
Use Conventional Commit style seen in history: `fix(search): ...`, `feat: ...`, `chore: ...`, `style: ...`.  
Keep commits scoped to one logical change.  
PRs should include:
- what changed and why,
- test evidence (command + result),
- any `.env`/config impact,
- sample request/response for API behavior changes.

## Security & Configuration Tips
Copy `.env.example` to `.env`; never commit secrets.  
`API_KEY`, model keys, and `DATABASE_URL` should be provided through environment variables.  
Do not hand-edit binary index files under `data/db` or `data/commentary_db`; regenerate via scripts when needed.
