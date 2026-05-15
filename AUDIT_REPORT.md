# EvidenceIQ Audit Report

Date: 2026-05-15

## Summary

EvidenceIQ was audited as a local-first FastAPI, Next.js, Docker, and privacy-aware sensitive-media application. The pass focused on immediate runtime breakage, malformed files, Docker/local setup, dependency exposure, upload safety, RBAC, audit logging, PII/EXIF handling, local AI claims, and documentation claims.

The repository now compiles, the FastAPI app starts under Uvicorn, the frontend installs/lints/builds, `pip-audit` and `npm audit` report no known vulnerabilities for the pinned dependency sets, and Compose syntax validates. Docker image builds could not be completed because Docker Desktop's Linux engine was not running on this host.

This audit implements privacy-aware controls and forensic-style controls. It does not certify legal admissibility, HIPAA/GDPR/PCI compliance, or formal chain-of-custody guarantees.

## Highest-Risk Findings and Fixes

### P0: Runtime and malformed-file breakage

- Fixed malformed/collapsed runtime and setup files:
  - `app/main.py`
  - `docker-compose.yml`
  - `Dockerfile`
  - `.env.example`
  - `.gitignore`
  - root `package.json`
  - `evidenceiq-ui/package.json`
- Fixed router registration issues that produced duplicated prefixes and unreachable API endpoints.
- Fixed import/startup fragility in media ingestion by making `python-magic` optional at runtime and adding `filetype` plus signature fallback.
- Fixed report and user/process route ordering so static routes are reached before dynamic `/{id}` routes.
- Replaced Docker healthcheck dependency on third-party `requests` with Python stdlib `urllib.request`.

### P0/P1: Secrets and production safety

- Added typed settings and startup validation in `app/config.py`.
- Production now rejects weak secrets, wildcard/dev CORS origins, and debug mode.
- API docs are disabled in production unless explicitly enabled.
- `.env`, local DBs, uploads, redacted media, thumbnails, reports, logs, ChromaDB data, and model/local artifacts are ignored by Git and Docker build context.
- Added `.dockerignore`.
- `.env.example` now uses placeholders only and documents required local setup.

### P1: Auth, JWT, RBAC, CORS, and headers

- Centralized JWT settings and bounded token expiry values.
- Added stricter missing-token behavior.
- Added security headers:
  - `X-Content-Type-Options`
  - `X-Frame-Options`
  - `Referrer-Policy`
  - `Permissions-Policy`
- Added production-safe exception handlers that avoid stack/body leakage.
- Added RBAC tests proving viewers cannot delete evidence, export reports, modify processing/tags, or access admin user endpoints.
- Added positive permission coverage for investigator, reviewer, and admin flows.

### P1: Upload and file safety

- Upload handling now enforces max file size, MIME checks, extension checks, server-side generated storage names, safe filename normalization, and duplicate-hash checks before writes.
- Added traversal protections for relative, absolute, encoded, and Windows-style paths.
- Added cleanup on failed upload processing.
- Added safe storage path resolver so file access/delete/thumbnail operations cannot escape `STORAGE_ROOT`.
- SHA256 is calculated from original upload bytes and persisted.
- File download and report generation verify persisted SHA256 before use.
- Original evidence is not modified during metadata redaction; redacted copies are written separately.

### P1/P2: PII, EXIF, reports, and audit logs

- Added metadata scrubbing for GPS, device serial/owner/software fields, and PII-like text before display/report use.
- Added regex fallback redaction for email, phone, SSN-like values, and medical-ID-like values when Presidio is unavailable or heavy local models are not installed.
- Added tests for EXIF GPS removal and PII redaction.
- Report PDFs now include full SHA256, hash verification status, report timestamp, generating user identity, redaction status, audit reference, and watermark text.
- Report export now fails if integrity verification fails.
- Added audit event type coverage for view/export.
- Added app-level append-only protections for audit log update/delete.
- Audit details are sanitized to reduce secret/token/password leakage.

### P1/P2: Local AI and telemetry claims

- Added a static test that fails if backend application code imports blocked cloud AI or telemetry SDKs without explicit review.
- Confirmed backend application code does not import OpenAI, Anthropic, Google GenAI, Azure AI, Sentry, LangSmith, or PostHog SDKs.
- ChromaDB is configured with anonymized telemetry disabled via `Settings(anonymized_telemetry=False)` and Docker/env defaults.
- README language was softened from unsupported absolute claims to local-first, privacy-aware wording.

### P1/P2: Dependencies and supply chain

- Updated vulnerable Python packages:
  - `fastapi==0.136.1`
  - `starlette==0.49.3`
  - `python-multipart==0.0.28`
  - `python-jose[cryptography]==3.5.0`
  - `pillow==12.2.0`
  - `sentence-transformers==5.5.0`
  - `transformers==5.0.0rc3`
  - `python-dotenv==1.2.2`
  - `bcrypt==4.2.1`
- Added `requirements-dev.txt` for test/audit/dev tooling.
- Fixed isolated `.venv` failure caused by `bcrypt 5.x` incompatibility with `passlib`.
- Added frontend lockfile reproducibility and fixed ESLint/Next 15 lint behavior.
- Added CI workflow and pre-commit configuration.

## Files Changed

```text
.env.example
.gitignore
.dockerignore
.github/workflows/ci.yml
.pre-commit-config.yaml
AUDIT_REPORT.md
Dockerfile
README.md
SECURITY.md
app/audit/models.py
app/audit/router.py
app/audit/service.py
app/auth/dependencies.py
app/auth/service.py
app/config.py
app/main.py
app/media/ingest.py
app/media/router.py
app/media/service.py
app/processing/embeddings.py
app/processing/extractor.py
app/processing/frames.py
app/processing/metadata.py
app/processing/router.py
app/processing/service.py
app/reports/builder.py
app/reports/router.py
app/reports/service.py
app/search/router.py
app/users/router.py
docker-compose.yml
evidenceiq-ui/app/globals.css
evidenceiq-ui/app/layout.tsx
evidenceiq-ui/components/media/MediaUploadZone.tsx
evidenceiq-ui/eslint.config.mjs
evidenceiq-ui/next.config.ts
evidenceiq-ui/package-lock.json
evidenceiq-ui/package.json
evidenceiq-ui/postcss.config.mjs
package-lock.json
package.json
requirements-dev.txt
requirements.txt
tests/test_auth.py
tests/test_local_ai_policy.py
tests/test_pii_metadata.py
tests/test_security_controls.py
tests/test_upload_safety.py
```

## Commands Run and Results

| Command | Result |
| --- | --- |
| `python -m compileall app tests` | Passed. |
| `pip install -r requirements.txt` | Passed. |
| `.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` | Passed. |
| `pip check` | Failed in the global Python environment because unrelated globally installed packages have conflicts (`camelot-py`, `langchain-*`, `llama-index-*`, `mcp`, `semantic-kernel`, `unstructured-client`). |
| `.venv\Scripts\python.exe -m pip check` | Passed: no broken requirements found. |
| `pytest -q` | Passed: 52 tests passed, 141 warnings. |
| `.venv\Scripts\python.exe -m pytest -q` | Passed: 52 tests passed, 119 warnings. |
| `pip-audit -r requirements.txt` | Passed: no known vulnerabilities found. |
| `uvicorn app.main:app --host 127.0.0.1 --port 8000` plus `/health` probe | Passed: `/health` returned HTTP 200. |
| `npm install` | Passed, root package audit showed 0 vulnerabilities. |
| `npm install --prefix evidenceiq-ui` | Passed, UI package audit showed 0 vulnerabilities. |
| `npm run lint` | Passed via root script delegating to UI ESLint. |
| `npm run build` | Passed with Next.js 15.5.18. |
| `npm audit` | Passed: 0 vulnerabilities. |
| `npm audit --prefix evidenceiq-ui --audit-level=moderate` | Passed: 0 vulnerabilities. |
| `docker compose config --quiet` | Passed with non-secret throwaway environment overrides. |
| `docker compose build` | Blocked by host Docker daemon: Docker Desktop Linux engine pipe was unavailable. |
| `docker build .` | Blocked by host Docker daemon: Docker Desktop Linux engine pipe was unavailable. |
| Static `rg` scan for cloud AI/telemetry imports | Backend app code had no blocked cloud AI or telemetry SDK imports. Frontend uses `axios` only for configured API calls. |
| Static `rg` scan for weak secret markers | Found intentional weak-secret blocklist entries and test password fixtures only; `.env` remains ignored and was not committed. |
| `git ls-files` review | No tracked uploads, local DBs, ChromaDB data, generated reports, local storage, or logs were identified. |

## Security Posture Before vs After

Before:

- Backend startup could fail due malformed files, import-time optional dependency failures, and duplicated router prefixes.
- Docker Compose and Dockerfile syntax/configuration were not reliable.
- Production startup could accept weak secrets, wildcard CORS, debug behavior, and exposed docs.
- Upload paths and filename handling had insufficient traversal hardening.
- PII/EXIF claims were stronger than the test coverage.
- Dependency audits found known vulnerabilities.
- Frontend lint/build path was incompatible with the installed Next.js generation.
- Privacy and chain-of-custody language overstated what the project could prove.

After:

- Backend compiles and starts cleanly, and `/health` responds.
- Frontend installs, lints, and builds.
- Compose syntax validates and Dockerfile is valid, non-root, and stdlib-healthchecked.
- Production settings reject weak secrets, wildcard/dev CORS, and debug behavior.
- Upload and file access paths have explicit traversal, extension, MIME, and storage-root enforcement.
- PII-aware metadata scrubbing and EXIF GPS redaction are covered by tests.
- RBAC-sensitive actions are covered by tests.
- Audit logging is broader and sanitized, with app-level append-only protection.
- Dependency audits for pinned backend and frontend dependencies are clean.
- README/SECURITY wording now describes privacy-aware and forensic-style controls without claiming formal compliance or certification.

## Remaining Manual Actions

- Start Docker Desktop or another Docker engine, then rerun:
  - `docker compose build`
  - `docker build .`
  - `docker compose up`
  - service health checks
- Replace local `.env` values with a fresh strong `SECRET_KEY` and explicit CORS origins before production use.
- Pull and test Ollama models intentionally; the optional `ollama-models` Compose profile no longer blocks API startup.
- Review whether `transformers==5.0.0rc3` is acceptable in your risk model. It clears the current audit finding, but should be moved to a stable 5.x release when available and retested.
- Run a real secret scanner such as `detect-secrets` or `gitleaks` in CI before accepting outside contributions.
- Review frontend token storage. The UI currently stores access and refresh tokens in `localStorage`; hardened production deployments should prefer secure, HttpOnly, same-site cookies.

## Remaining Risks Not Fixed

- Docker image build/runtime health is not validated on this host because the Docker daemon was unavailable.
- Audit logs are append-only only at the application layer. They are not WORM storage and can still be altered by direct database access.
- SQLite is acceptable for local/demo workflows but is not a production HA database.
- PII redaction is best-effort. Regex fallback and optional Presidio support do not guarantee complete PII removal.
- ChromaDB brings telemetry-related transitive packages; application code disables anonymized telemetry, but deployments should verify dependency behavior and network egress policy.
- Generated reports are forensic-style summaries, not certified legal evidence packets.
- Formal GDPR/HIPAA/PCI compliance and forensic admissibility are not established by this audit.
- Several deprecation warnings remain around SQLAlchemy declarative base, Pydantic class-based config, and timezone-naive datetimes.
- Local AI model downloads and embedding model loads may require network access unless pre-cached for air-gapped deployments.

## Recommended Next Commit Message

```text
Harden startup, uploads, Docker, deps, and privacy claims
```
