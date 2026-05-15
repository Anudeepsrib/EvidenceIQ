import os
from pathlib import Path
from typing import List

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


WEAK_SECRET_MARKERS = {
    "your-super-secret-key-change-this-in-production",
    "change-me",
    "change-me-in-production",
    "secret",
    "dev-secret",
    "password",
}

DEV_SECRET_KEY = "dev-only-evidenceiq-secret-not-for-production-000000"
DEFAULT_DEV_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables or .env."""

    # Application
    app_name: str = Field("EvidenceIQ", description="Application name")
    app_env: str = Field("development", description="Environment: development | staging | production")
    app_version: str = Field("1.0.0", description="Semantic version")
    app_host: str = Field("0.0.0.0", description="Bind host for uvicorn")
    app_port: int = Field(8000, description="Bind port for uvicorn")
    log_level: str = Field("INFO", description="Python logging level")
    debug: bool = Field(False, description="Debug mode")
    enable_api_docs: bool = Field(False, description="Enable API docs in production")

    # Security
    secret_key: str = Field(
        DEV_SECRET_KEY,
        description="JWT secret key - generate with: openssl rand -hex 32",
    )
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(60, description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(7, description="Refresh token expiration in days")
    password_min_length: int = Field(8, description="Minimum password length")

    # CORS
    cors_origins: str = Field(
        DEFAULT_DEV_CORS_ORIGINS,
        description="Comma-separated allowed origins"
    )

    # Database
    database_url: str = Field(
        "sqlite:///./evidenceiq.db",
        description="Database URL (SQLite default, PostgreSQL ready)"
    )

    # Storage
    storage_root: str = Field(
        "./storage",
        description="Root path for file storage"
    )
    max_file_size_mb: int = Field(500, description="Maximum file upload size in MB")

    # AI / Ollama
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

    # Vector Store
    chroma_db_path: str = Field(
        "./chromadb_data",
        description="Path for ChromaDB persistent storage"
    )
    embedding_model: str = Field(
        "sentence-transformers/clip-ViT-B-32",
        description="CLIP model for image embeddings"
    )

    # Processing
    video_frame_interval_seconds: int = Field(
        1,
        description="Extract video frames every N seconds"
    )
    thumbnail_max_size: int = Field(512, description="Max thumbnail dimension in pixels")
    enable_pii_scrubbing: bool = Field(True, description="Enable PII scrubbing from metadata")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(60, description="Rate limit per user per minute")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"development", "staging", "production", "test"}:
            raise ValueError("APP_ENV must be development, staging, production, or test")
        return normalized

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.upper().strip()
        if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
        return normalized

    @field_validator("jwt_algorithm")
    @classmethod
    def validate_jwt_algorithm(cls, value: str) -> str:
        if value != "HS256":
            raise ValueError("Only HS256 is supported for local JWT signing")
        return value

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_access_token_expiry(cls, value: int) -> int:
        if value < 5 or value > 24 * 60:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 5 and 1440")
        return value

    @field_validator("refresh_token_expire_days")
    @classmethod
    def validate_refresh_token_expiry(cls, value: int) -> int:
        if value < 1 or value > 30:
            raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be between 1 and 30")
        return value

    @field_validator("password_min_length")
    @classmethod
    def validate_password_min_length(cls, value: int) -> int:
        if value < 8 or value > 128:
            raise ValueError("PASSWORD_MIN_LENGTH must be between 8 and 128")
        return value

    @field_validator("max_file_size_mb")
    @classmethod
    def validate_max_file_size(cls, value: int) -> int:
        if value < 1 or value > 2048:
            raise ValueError("MAX_FILE_SIZE_MB must be between 1 and 2048")
        return value

    @model_validator(mode="after")
    def validate_security_posture(self):
        if self.is_production:
            if self.debug:
                raise ValueError("DEBUG must be false in production")

            if self._is_weak_secret(self.secret_key):
                raise ValueError("Production requires a strong SECRET_KEY generated with openssl rand -hex 32")

            origins = self.cors_origin_list
            if not origins or "*" in origins or self.cors_origins == DEFAULT_DEV_CORS_ORIGINS:
                raise ValueError("Production requires explicit non-wildcard CORS_ORIGINS")

        return self

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS_ORIGINS into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def cors_allow_credentials(self) -> bool:
        """Do not allow credentials when wildcard CORS is configured for local experiments."""
        return "*" not in self.cors_origin_list

    @property
    def api_docs_enabled(self) -> bool:
        """API docs are development-only unless explicitly enabled for production."""
        return not self.is_production or self.enable_api_docs

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

    @staticmethod
    def _is_weak_secret(secret_key: str) -> bool:
        normalized = secret_key.strip().lower()
        if len(secret_key.strip()) < 32:
            return True
        if normalized in WEAK_SECRET_MARKERS:
            return True
        return any(
            marker in normalized
            for marker in ("change-me", "dev-secret", "your-super-secret", "replace-with", "secret")
        )


# Global settings instance
settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.resolved_storage_path / "uploads", exist_ok=True)
os.makedirs(settings.resolved_storage_path / "redacted", exist_ok=True)
os.makedirs(settings.resolved_storage_path / "thumbnails", exist_ok=True)
