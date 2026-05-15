<div align="center">
  <img src="static/logo.png" alt="EvidenceIQ Logo" width="150" style="border-radius: 20%; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
  
  <h1 style="margin-top: 0;">EvidenceIQ 🔬</h1>
  
  <p><b>"Clone it. Run it. Own it. Your media never leaves your machine."</b></p>
  
  <p>A privacy-first local reference implementation for organizations handling sensitive media, PII-aware metadata controls, RBAC, local AI processing, and audit trails.</p>

  <p>
    <a href="https://github.com/Anudeepsrib/EvidenceIQ">
      <img src="https://img.shields.io/github/stars/Anudeepsrib/EvidenceIQ?style=for-the-badge&logo=github" alt="GitHub stars" />
    </a>
    <a href="https://github.com/Anudeepsrib/EvidenceIQ">
      <img src="https://img.shields.io/github/forks/Anudeepsrib/EvidenceIQ?style=for-the-badge&logo=github" alt="GitHub forks" />
    </a>
    <a href="https://github.com/Anudeepsrib/EvidenceIQ/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/Anudeepsrib/EvidenceIQ?style=for-the-badge" alt="License" />
    </a>
  </p>

  <p>
    <a href="#-core-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#%EF%B8%8F-tech-stack">Tech Stack</a> •
    <a href="#-models--llms">Models</a> •
    <a href="#-who-uses-evidenceiq">Use Cases</a>
  </p>
  
  <a href="https://github.com/Anudeepsrib/EvidenceIQ">
    <img src="https://github-readme-stats.vercel.app/api/pin/?username=Anudeepsrib&repo=EvidenceIQ&theme=radical&show_owner=true" alt="Readme Card" />
  </a>
</div>

---

## 🔒 Local-First Privacy Posture

EvidenceIQ is built for local processing by default. AI inference is intended to run through local Ollama, while optional external integrations should be explicitly configured and reviewed before use.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🚫 No Cloud AI by Default</h3>
      <p>No cloud vision SDKs are imported by the backend. Local AI inference runs through Ollama unless a future integration is explicitly added and reviewed.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🧠 Local AI Processing</h3>
      <p>Vision models (LLaVA, BakLLaVA, Moondream) and CLIP embeddings run on your hardware. Keep model downloads and package installs in mind for air-gapped deployments.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>💾 Sovereign SQLite</h3>
      <p>All data, metadata, tags, and audit logs live inside a single <code>evidenceiq.db</code> file that you alone own and control.</p>
    </td>
    <td width="50%" valign="top">
      <h3>📡 No App Telemetry</h3>
      <p>Application code does not import analytics or telemetry SDKs, and ChromaDB is configured with anonymized telemetry disabled. Verify dependencies and deployment settings before asserting a formal zero-telemetry posture.</p>
    </td>
  </tr>
</table>

---

## ✨ Core Features

<table>
  <tr>
    <td width="33%" valign="top">
      <b>🔍 Multimodal Vision</b><br/>
      Automatic classification, description, and entity tagging for images and video frames. Supports JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, and PDF.
    </td>
    <td width="33%" valign="top">
      <b>🔗 Chain of Custody</b><br/>
      SHA256 hashing on every upload. Hash verified on file access. Application-level append-only audit logs for forensic-style integrity controls.
    </td>
    <td width="33%" valign="top">
      <b>🔐 RBAC Access Control</b><br/>
      Four-tier role system (Admin, Investigator, Reviewer, Viewer) with granular permissions for upload, tag, export, redact, and delete.
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top">
      <b>🧲 Semantic Search</b><br/>
      CLIP-powered similarity search via local ChromaDB. Find media by meaning, not just keywords.
    </td>
    <td width="33%" valign="top">
      <b>🛡️ PII Scrubbing</b><br/>
      EXIF extraction with sensitive metadata removed before display. Redacted copies are separate — originals are never modified.
    </td>
    <td width="33%" valign="top">
      <b>📄 Report Generation</b><br/>
      Generate watermarked PDF reports stamped "CONFIDENTIAL - EvidenceIQ" with evidence hashes and audit references.
    </td>
  </tr>
</table>

---

## 👥 Who Uses EvidenceIQ

<table>
  <tr>
    <td width="25%" valign="top">
      <b>⚖️ Legal Firms</b><br/>
      Organize deposition recordings, redact sensitive metadata, generate chain-of-custody reports.
    </td>
    <td width="25%" valign="top">
      <b>🏢 HR Departments</b><br/>
      Document incident reports, ensure metadata integrity, controlled role-based access.
    </td>
    <td width="25%" valign="top">
      <b>🏥 Healthcare</b><br/>
      Process sensitive imaging locally with PII-aware controls. HIPAA claims require a formal compliance review.
    </td>
    <td width="25%" valign="top">
      <b>🔎 Compliance Teams</b><br/>
      Review surveillance stills, automated tagging, audit trail preservation for regulatory compliance.
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Clone and Configure

```bash
git clone https://github.com/Anudeepsrib/EvidenceIQ.git
cd EvidenceIQ
cp .env.example .env
```

Edit `.env` and set a strong secret:

```bash
openssl rand -hex 32
```

### Backend

```bash
python -m venv .venv

source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```bash
npm install --prefix evidenceiq-ui
npm run dev --prefix evidenceiq-ui
```

Open [http://localhost:3000](http://localhost:3000) for the UI and [http://localhost:8000/docs](http://localhost:8000/docs) for API docs in development.

### Ollama Models

Install [Ollama](https://ollama.com) and pull only the models you plan to use:

```bash
ollama pull llava
ollama pull bakllava
ollama pull moondream
ollama pull mistral
```

### Docker Compose

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY with openssl rand -hex 32
docker compose up --build

# Optional model pre-pull profile
docker compose --profile models run --rm ollama-models
```

### Tests and Checks

```bash
python -m compileall app tests
pytest
npm run lint
npm run build
docker compose config
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   User Upload   │ JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, PDF
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                      INGEST PIPELINE                     │
│  • MIME and extension validation                         │
│  • Filename sanitization (path traversal protection)     │
│  • SHA256 hash computation (chain of custody)            │
│  • UUID-based internal storage paths                     │
│  • EXIF extraction + PII-aware display scrubbing         │
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
│  • Description generation (2-3 factual sentences)        │
│  • Entity tagging (people, objects, location, etc.)      │
│                                                          │
│  Models: LLaVA, BakLLaVA, Moondream via Ollama (local)  │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                       │
│  • Media items + metadata                                │
│  • Tags extracted from vision pipeline                   │
│  • Users + RBAC                                          │
│  • Append-only audit logs                                │
└──────────────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Search │ │Reports │ │ Audit  │
└────────┘ └────────┘ └────────┘
```

---

## 🛠️ Tech Stack

<table>
  <tr>
    <th width="50%">Frontend (Next.js App Router)</th>
    <th width="50%">Backend (Data Engine)</th>
  </tr>
  <tr>
    <td valign="top">
      <ul>
        <li><b>Framework:</b> Next.js 15</li>
        <li><b>Styling:</b> Tailwind CSS v3 + Lucide Icons</li>
        <li><b>State:</b> TanStack Query + Zustand</li>
        <li><b>Forms:</b> React Hook Form + Zod</li>
        <li><b>Language:</b> TypeScript</li>
      </ul>
    </td>
    <td valign="top">
      <ul>
        <li><b>API:</b> FastAPI (Python 3.11+)</li>
        <li><b>Database:</b> SQLAlchemy + Alembic</li>
        <li><b>AI Orchestration:</b> Ollama SDK</li>
        <li><b>Vector Store:</b> ChromaDB + CLIP</li>
        <li><b>PII Detection:</b> Presidio Analyzer</li>
        <li><b>Logging:</b> Structlog</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🧠 Models & LLMs

We recommend local models for optimal media analysis. Vision models are required; text models enhance metadata summarization.

| Model | Type | Resource Size | Best Use Case |
|-------|------|---------------|---------------|
| **LLaVA** | 🖼️ Vision | `~4GB RAM` | Default vision analysis. Best accuracy for classification and description. |
| **BakLLaVA** | 🖼️ Vision | `~4GB RAM` | Alternative vision model. Strong entity tagging. |
| **Moondream** | 🖼️ Vision | `~2GB RAM` | Lightweight vision. Ideal for older hardware or edge devices. |
| **Mistral 7B** | 📝 Text | `~4GB RAM` | Metadata summarization, report narrative generation. |

---

## 🔐 Security Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🎫 JWT Authentication</h3>
      <p>Configurable bounded access and refresh token lifetimes. Secure session management without cloud dependency.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ RBAC Enforcement</h3>
      <p>Hidden (not disabled) permissions — unauthorized requests receive a generic 403. No information leakage.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>⏱️ Rate Limiting</h3>
      <p>Configurable per-client rate limiting via SlowAPI. Protection against abuse without external infrastructure.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🧱 Defense in Depth</h3>
      <p>Path traversal protection (UUID storage), SQL injection prevention (ORM parameterized queries), masked stack traces in production.</p>
    </td>
  </tr>
</table>

---

## 🔑 RBAC Matrix

| Role | Upload | View | Tag | Export | Redact | Manage Users | Delete |
|------|--------|------|-----|--------|--------|--------------|--------|
| `admin` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `investigator` | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| `reviewer` | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `viewer` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 📡 API Overview

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

---

## ⚙️ Configuration

Your instance can be customized entirely via the `.env` file:

```env
# Security (required - generate with: openssl rand -hex 32)
SECRET_KEY=replace-with-64-hex-character-random-value

# Environment
APP_ENV=development

# Local Database Persistence
DATABASE_URL=sqlite:///./evidenceiq.db
STORAGE_ROOT=./storage

# AI Provider targeting a local Ollama instance
OLLAMA_BASE_URL=http://localhost:11434

# Vector Store
CHROMA_DB_PATH=./chromadb_data

# Upload Limits
MAX_FILE_SIZE_MB=500

# JWT Configuration
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## ⚠️ Disclaimer
**General Use Only:** EvidenceIQ is an open-source software project. It implements privacy-aware and forensic-style controls, but it does **not** constitute legal advice, formal compliance certification, or a guarantee of forensic admissibility. Organizations with specific compliance requirements should consult qualified legal, compliance, and cybersecurity professionals.

---

<div align="center">
  <p>Built with 🔒 for teams who refuse to compromise on privacy.</p>
  <p><b>EvidenceIQ:</b> Local intelligence. Private by design.</p>
</div>
