"""
EvidenceIQ Configuration
Pydantic Settings for environment-based configuration.
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """
    All application configuration loaded from environment variables / .env file.
    Zero external API calls - fully air-gap capable.
    """

    # ── Application ──────────────────────────────────────────────
    app_name: str = Field("EvidenceIQ", description="Application name")
    app_env: str = Field("development", description="Environment: development | staging | production")
    app_version: str = Field("1.0.0", description="Semantic version")
    app_host: str = Field("0.0.0.0", description="Bind host for uvicorn")
    app_port: int = Field(8000, description="Bind port for uvicorn")
    log_level: str = Field("INFO", description="Python logging level")
    debug: bool = Field(False, description="Debug mode")

    # ── Security ───────────────────────────────────────────────────
    secret_key: str = Field(..., description="JWT secret key - generate with: openssl rand -hex 32")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(60, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration in days")
    password_min_length: int = Field(8, description="Minimum password length")

    # ── CORS ───────────────────────────────────────────────────────
    cors_origins: str = Field(
        "http://localhost:3000,http://localhost:8000",
        description="Comma-separated allowed origins"
    )

    # ── Database ───────────────────────────────────────────────────
    database_url: str = Field(
        "sqlite:///./evidenceiq.db",
        description="Database URL (SQLite default, PostgreSQL ready)"
    )

    # ── Storage ────────────────────────────────────────────────────
    storage_root: str = Field(
        "./storage",
        description="Root path for file storage"
    )
    max_file_size_mb: int = Field(500, description="Maximum file upload size in MB")

    # ── AI / Ollama (Local Only) ───────────────────────────────────
    ollama_base_url: str = Field(
        "http://localhost:11434",
        description="Ollama API base URL"
    )
    vision_model_default: str = Field("llava", description="Default vision model")
    llm_model: str = Field("mistral", description="LLM for metadata summarization")
    available_vision_models: str = Field(
        "llava,bakllava,moondream",
        description="Comma-separated list of available vision models"
    )

    # ── Vector Store (ChromaDB) ────────────────────────────────────
    chroma_db_path: str = Field(
        "./chromadb_data",
        description="Path for ChromaDB persistent storage"
    )
    embedding_model: str = Field(
        "sentence-transformers/clip-ViT-B-32",
        description="CLIP model for image embeddings"
    )

    # ── Processing ─────────────────────────────────────────────────
    video_frame_interval_seconds: int = Field(
        1,
        description="Extract video frames every N seconds"
    )
    thumbnail_max_size: int = Field(512, description="Max thumbnail dimension in pixels")
    enable_pii_scrubbing: bool = Field(True, description="Enable PII scrubbing from metadata")

    # ── Rate Limiting ──────────────────────────────────────────────
    rate_limit_requests_per_minute: int = Field(60, description="Rate limit per user per minute")

    # ── Pydantic Config ────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Properties ───────────────────────────────────────────────────
    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def resolved_storage_path(self) -> Path:
        """Resolve storage path relative to project root."""
        p = Path(self.storage_root)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / p
        return p.resolve()

    @property
    def resolved_chroma_path(self) -> Path:
        """Resolve ChromaDB path relative to project root."""
        p = Path(self.chroma_db_path)
        if not p.is_absolute():
            p = Path(__file__).parent.parent / p
        return p.resolve()

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def available_vision_models_list(self) -> List[str]:
        """Parse available vision models into a list."""
        return [m.strip() for m in self.available_vision_models.split(",") if m.strip()]


# Global settings instance
settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.resolved_storage_path / "uploads", exist_ok=True)
os.makedirs(settings.resolved_storage_path / "redacted", exist_ok=True)
os.makedirs(settings.resolved_storage_path / "thumbnails", exist_ok=True)
