# AgentTrust

Backend-first foundation for the AgentTrust security gateway project.

## Local setup

```bash
cd agenttrust
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -e '.[dev]'
```

## Run the app

```bash
. .venv/bin/activate
uvicorn app.main:app --reload
```

## Validation

```bash
. .venv/bin/activate
pytest -q
ruff check .
```

## Environment

Copy `.env.example` to `.env` and adjust values as needed.
