"""
EvidenceIQ - Main Application
Privacy-first local multimodal intelligence platform.
Zero external API calls. Fully air-gap capable.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import setup_rate_limiting

# Import routers
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.media.router import router as media_router
from app.processing.router import router as processing_router
from app.search.router import router as search_router
from app.reports.router import router as reports_router
from app.audit.router import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"🚀 Starting EvidenceIQ v{settings.app_version} ({settings.app_env})")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Ensure storage directories exist
    from pathlib import Path
    for subdir in ["uploads", "redacted", "thumbnails", "reports"]:
        (settings.resolved_storage_path / subdir).mkdir(parents=True, exist_ok=True)
    print("✅ Storage directories initialized")
    
    print(f"📁 Storage root: {settings.resolved_storage_path}")
    print(f"🔐 Authentication: JWT (expires in {settings.access_token_expire_minutes} min)")
    print(f"🤖 AI Models: Ollama @ {settings.ollama_base_url}")
    print(f"🔍 Vector Store: ChromaDB @ {settings.resolved_chroma_path}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down EvidenceIQ")


# Create FastAPI app
app = FastAPI(
    title="EvidenceIQ API",
    description="""
    Privacy-first local multimodal intelligence platform.
    
    **Key Features:**
    - Zero cloud transmission - fully air-gap capable
    - RBAC-enforced access control (admin, investigator, reviewer, viewer)
    - Local vision models via Ollama (LLaVA, BakLLaVA, moondream)
    - Semantic search with CLIP embeddings
    - PII scrubbing from metadata
    - Evidence report generation with chain of custody
    
    **Security:**
    - JWT authentication with 60-minute expiration
    - Rate limiting (60 req/min)
    - SHA256 file hashing for chain of custody
    - Append-only audit logging
    """,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Structured logging middleware
app.add_middleware(LoggingMiddleware)

# Rate limiting
setup_rate_limiting(app)


# Global exception handler - no stack traces in production
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions - never expose internals."""
    from app.middleware.logging import logger
    
    # Log full error details internally
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
    )
    
    # Return safe error response
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An internal error occurred. Please try again later."
            }
        )
    else:
        # In development, include more details
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": str(exc),
                "type": type(exc).__name__
            }
        )


# Health check endpoint (no auth required)
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.app_env,
        "features": {
            "auth": True,
            "media_upload": True,
            "vision_processing": True,
            "semantic_search": True,
            "audit_logging": True
        }
    }


# Root endpoint
@app.get("/")
def root():
    """API root - redirects to documentation."""
    return {
        "message": "EvidenceIQ API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["User Management"])
app.include_router(media_router, prefix="/media", tags=["Media"])
app.include_router(processing_router, prefix="/process", tags=["Processing"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(audit_router, prefix="/audit", tags=["Audit"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
