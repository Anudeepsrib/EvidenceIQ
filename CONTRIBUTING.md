# Contributing

## Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Run `pip install -r requirements-dev.txt`.
3. Run `npm ci --prefix evidenceiq-ui`.
4. Copy `.env.example` to `.env` and replace `SECRET_KEY`.

## Before opening a pull request

```bash
ruff check .
pytest
npm run lint
npm run build
```

Keep changes focused, add the smallest relevant test for behavior changes, and never commit
media, databases, generated reports, credentials, or local environment files.

Security issues should follow [SECURITY.md](SECURITY.md), not a public issue.
