<div align="center">
  <img src="static/logo.png" alt="EvidenceIQ Logo" width="150" style="border-radius: 20%; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
  
  <h1 style="margin-top: 0;">EvidenceIQ 🔬</h1>
  
  <p><b>"Clone it. Run it. Own it. Your media never leaves your machine."</b></p>
  
  <p>A privacy-first, fully local multimodal intelligence platform for organizations handling sensitive media — zero external API calls, fully air-gap capable.</p>

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

## 🔒 The Zero-Cloud Promise

EvidenceIQ is built on the philosophy of complete data sovereignty. Your sensitive media should never leave your infrastructure.

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>🚫 Zero External API Calls</h3>
      <p>No cloud vision APIs (Google, Azure, AWS). All AI inference runs locally via Ollama. Your media never traverses networks you don't control.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🧠 Local AI Processing</h3>
      <p>Vision models (LLaVA, BakLLaVA, Moondream) and CLIP embeddings run entirely on your hardware. Zero data transmission.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>💾 Sovereign SQLite</h3>
      <p>All data, metadata, tags, and audit logs live inside a single <code>evidenceiq.db</code> file that you alone own and control.</p>
    </td>
    <td width="50%" valign="top">
      <h3>📡 Zero Telemetry</h3>
      <p>No hidden analytics, tracking, or data harvesting. Fully air-gap capable — works entirely offline after initial setup.</p>
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
      SHA256 hashing on every upload. Hash verified on every access. Append-only audit logs for forensic-level integrity.
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
      Automatic EXIF extraction and PII detection via Presidio. Redacted copies are separate — originals are never modified.
    </td>
    <td width="33%" valign="top">
      <b>📄 Report Generation</b><br/>
      Generate watermarked PDF reports stamped "CONFIDENTIAL — EvidenceIQ" with full audit trail lineage.
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
      Process patient imaging internally with zero PHI transmission. HIPAA-friendly by design.
    </td>
    <td width="25%" valign="top">
      <b>🔎 Compliance Teams</b><br/>
      Review surveillance stills, automated tagging, audit trail preservation for regulatory compliance.
    </td>
  </tr>
</table>

---

## 🚀 Quick Start

Get up and running locally in under 10 minutes.

### 1. Pull Vision Models
Ensure you have [Ollama](https://ollama.com) installed and pull the required models:
```bash
# Vision models
ollama pull llava           # Default vision model
ollama pull bakllava        # Alternative vision model
ollama pull moondream       # Lightweight vision model

# Text model
ollama pull mistral         # For metadata summarization
```

### 2. Clone & Bootstrap

**Docker Compose (Recommended):**
```bash
git clone https://github.com/Anudeepsrib/EvidenceIQ.git
cd EvidenceIQ

# Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY: openssl rand -hex 32

# Start all services
docker-compose up -d

# Wait for Ollama to pull models (first start takes time)
docker-compose logs -f ollama
```

**Development Setup:**
```bash
git clone https://github.com/Anudeepsrib/EvidenceIQ.git
cd EvidenceIQ

# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head

# Frontend
cd evidenceiq-ui
npm install
```

### 3. Launch
Launch two terminal windows to start the backend engine and frontend interface.

**Terminal 1 — FastAPI Backend:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 — Next.js Frontend:**
```bash
cd evidenceiq-ui
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the UI and [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

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
│  • MIME validation (python-magic)                        │
│  • Filename sanitization (path traversal protection)     │
│  • SHA256 hash computation (chain of custody)            │
│  • UUID-based internal storage paths                     │
│  • EXIF extraction + PII scrubbing (presidio-analyzer)   │
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
      <p>60-minute access tokens, 7-day refresh tokens. Secure session management without cloud dependency.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🛡️ RBAC Enforcement</h3>
      <p>Hidden (not disabled) permissions — unauthorized requests receive a generic 403. No information leakage.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>⏱️ Rate Limiting</h3>
      <p>60 requests per minute per user via SlowAPI. Protection against abuse without external infrastructure.</p>
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
# Security (REQUIRED - generate with: openssl rand -hex 32)
SECRET_KEY=your-generated-secret-key

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
**General Use Only:** EvidenceIQ is an open-source software project. It does **not** constitute legal advice, certification, or guarantee of forensic admissibility. Organizations with specific compliance requirements should consult qualified legal and cybersecurity professionals. Always validate chain-of-custody workflows against your jurisdiction's requirements.

---

<div align="center">
  <p>Built with 🔒 for teams who refuse to compromise on privacy.</p>
  <p><b>EvidenceIQ:</b> Local intelligence. Private by design.</p>
</div>
