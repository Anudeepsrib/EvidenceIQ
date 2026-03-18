# EvidenceIQ

**Privacy-first local multimodal intelligence platform. Zero external API calls. Fully air-gap capable.**

EvidenceIQ transforms media analysis for organizations handling sensitive materials — legal firms managing deposition recordings, HR departments storing incident documentation, healthcare providers with patient imaging, and compliance teams reviewing surveillance stills.

> ⚠️ **The problem with cloud-based media AI:** Every upload to cloud vision APIs creates a privacy liability. Data leaves your infrastructure, traverses networks you don't control, and resides on servers subject to foreign jurisdictions. For organizations handling sensitive media, this isn't just risky — it's often non-compliant with GDPR, HIPAA, and legal discovery rules.

## Who Uses EvidenceIQ

| Organization | Use Case |
|-------------|----------|
| **Legal Firms** | Organize deposition recordings, redact sensitive metadata, generate chain-of-custody reports |
| **HR Departments** | Document incident reports, ensure metadata integrity, controlled access |
| **Healthcare** | Process patient imaging internally, zero PHI transmission |
| **Compliance Teams** | Review surveillance stills, automated tagging, audit trail preservation |

## Architecture

```
┌─────────────────┐
│   User Upload   │ JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, PDF
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                      INGEST PIPELINE                       │
│  • MIME validation (python-magic)                          │
│  • Filename sanitization (path traversal protection)       │
│  • SHA256 hash computation (chain of custody)               │
│  • UUID-based internal storage paths                       │
│  • EXIF extraction + PII scrubbing (presidio-analyzer)     │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────┐         ┌──────────────────────────┐
│  CLIP EMBEDDINGS     │────────▶│  ChromaDB (local)        │
│  (sentence-          │         │  Semantic vector store   │
│   transformers)      │         │                          │
└──────────────────────┘         └──────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                  VISION PIPELINE                         │
│  • Classification (document | photograph | screenshot    │
│    | diagram | surveillance | medical | chart | mixed)   │
│  • Description generation (2-3 factual sentences)      │
│  • Entity tagging (people, objects, location, etc.)      │
│                                                          │
│  Models: LLaVA, BakLLaVA, Moondream via Ollama (local)   │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                       │
│  • Media items + metadata                              │
│  • Tags extracted from vision pipeline                   │
│  • Users + RBAC                                        │
│  • Append-only audit logs                              │
└──────────────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Search │ │Reports │ │ Audit  │
└────────┘ └────────┘ └────────┘
```

## RBAC Matrix

| Role | Upload | View | Tag | Export | Redact | Manage Users | Delete |
|------|--------|------|-----|--------|--------|--------------|--------|
| `admin` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `investigator` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `reviewer` | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `viewer` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

## Supported Media Types

| Type | MIME | Processing |
|------|------|------------|
| JPEG | image/jpeg | EXIF extraction, vision analysis, CLIP embedding |
| PNG | image/png | Vision analysis, CLIP embedding |
| TIFF | image/tiff | EXIF extraction, vision analysis, CLIP embedding |
| WEBP | image/webp | Vision analysis, CLIP embedding |
| MP4 | video/mp4 | Frame extraction (1fps), each frame analyzed |
| MOV | video/quicktime | Frame extraction (1fps), each frame analyzed |
| AVI | video/x-msvideo | Frame extraction (1fps), each frame analyzed |
| PDF | application/pdf | Image extraction, each image analyzed |

## Local Model Setup

Pull required Ollama models before first use:

```bash
# Vision models
ollama pull llava          # Default vision model
ollama pull bakllava       # Alternative vision model
ollama pull moondream      # Lightweight vision model

# Text model
ollama pull mistral        # For metadata summarization
```

## Chain of Custody

EvidenceIQ maintains forensic-level integrity:

1. **SHA256 Hashing:** Every file is hashed on upload. Hash verified on every access.
2. **Redaction Audit Trail:** Original files are never modified. Redacted copies are separate files with new hashes.
3. **Report Watermarking:** Generated PDFs contain "CONFIDENTIAL — EvidenceIQ" watermark on every page.
4. **Append-Only Audit Log:** All permission-sensitive actions logged to tamper-evident audit table.

**Why this matters for legal admissibility:** Courts increasingly require proof that digital evidence hasn't been tampered with. EvidenceIQ's hash chain and audit logs provide this foundation.

## Zero External Calls Guarantee

EvidenceIQ makes **zero external API calls** after initialization:

- ❌ No cloud vision APIs (Google, Azure, AWS)
- ❌ No external embedding services
- ❌ No telemetry or analytics
- ✅ CLIP embeddings run locally
- ✅ Vision models run via local Ollama
- ✅ Vector store (ChromaDB) is local and persistent

Fully air-gap capable. Works entirely offline after initial setup.

## Setup Instructions

### Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/anudeepsrib/evidenceiq.git
cd evidenceiq

# 2. Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY: openssl rand -hex 32

# 3. Start services
docker-compose up -d

# 4. Wait for Ollama to pull models (first start takes time)
docker-compose logs -f ollama

# 5. Access API at http://localhost:8000
```

### First Admin User Creation

```bash
# Create admin user via API
curl -X POST http://localhost:8000/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure-password-123",
    "email": "admin@example.com",
    "role": "admin"
  }'
```

### Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edit .env

# 4. Run database migrations
alembic upgrade head

# 5. Start development server
uvicorn app.main:app --reload
```

## API Overview

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Health check | None |
| `/auth/login` | POST | Login, get tokens | None |
| `/auth/me` | GET | Current user info | JWT |
| `/users` | GET/POST | User management | Admin |
| `/media/upload` | POST | Upload media | Upload permission |
| `/media/{id}` | GET | Media details | View permission |
| `/media/{id}/file` | GET | Stream file | View permission |
| `/media/{id}/redact` | POST | Redact metadata | Redact permission |
| `/process/{id}` | POST | Run vision pipeline | Tag permission |
| `/search/semantic` | GET | Semantic search | View permission |
| `/search/tags` | GET | Tag-based search | View permission |
| `/reports/generate` | POST | Generate PDF report | Export permission |
| `/audit/logs` | GET | Query audit logs | Audit permission |

## Security Features

- **JWT Authentication:** 60-minute access tokens, 7-day refresh tokens
- **Role-Based Access Control:** Hidden (not disabled) — 403 with generic message
- **Rate Limiting:** 60 requests per minute per user
- **File Integrity:** SHA256 hash verified on every file access
- **Path Traversal Protection:** UUID-based internal paths, sanitized filenames
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **No Stack Traces:** Global exception handler masks internals in production

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | **Required** | JWT signing key (generate with `openssl rand -hex 32`) |
| `APP_ENV` | `development` | Environment: development, staging, production |
| `DATABASE_URL` | `sqlite:///./evidenceiq.db` | Database connection string |
| `STORAGE_ROOT` | `./storage` | File storage directory |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `CHROMA_DB_PATH` | `./chromadb_data` | Vector store directory |
| `MAX_FILE_SIZE_MB` | `500` | Maximum upload size |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT expiration |

## License

MIT License — See LICENSE file for details.

---

**EvidenceIQ:** Local intelligence. Private by design.
