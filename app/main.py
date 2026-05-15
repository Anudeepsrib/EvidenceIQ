"""
EvidenceIQ - Main Application
Privacy-aware local multimodal intelligence platform.
"""
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
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
    print(f"Starting EvidenceIQ v{settings.app_version} ({settings.app_env})")
    
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Ensure storage directories exist
    from pathlib import Path
    for subdir in ["uploads", "redacted", "thumbnails", "reports", "chromadb"]:
        (settings.resolved_storage_path / subdir).mkdir(parents=True, exist_ok=True)
    print("Storage directories initialized")
    
    print(f"Storage root: {settings.resolved_storage_path}")
    print(f"Authentication: JWT (expires in {settings.access_token_expire_minutes} min)")
    print(f"AI models: Ollama @ {settings.ollama_base_url}")
    print(f"Vector store: ChromaDB @ {settings.resolved_chroma_path}")
    
    yield
    
    # Shutdown
    print("Shutting down EvidenceIQ")


# Create FastAPI app
app = FastAPI(
    title="EvidenceIQ API",
    description="""
    Privacy-aware local multimodal intelligence reference implementation.
    
    **Key Features:**
    - Local-first AI processing through Ollama
    - RBAC-enforced access control (admin, investigator, reviewer, viewer)
    - Local vision models via Ollama (LLaVA, BakLLaVA, moondream)
    - Semantic search with CLIP embeddings
    - PII-aware metadata controls
    - Evidence reports with forensic-style hashes and audit references
    
    **Security:**
    - JWT authentication with bounded expiration
    - Configurable rate limiting
    - SHA256 file hashing for original uploads
    - Application-level append-only audit logging
    """,
    version=settings.app_version,
    docs_url="/docs" if settings.api_docs_enabled else None,
    redoc_url="/redoc" if settings.api_docs_enabled else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# Structured logging middleware
app.add_middleware(LoggingMiddleware)

# Rate limiting
setup_rate_limiting(app)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Attach conservative browser security headers to every response."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return structured HTTP errors without FastAPI's nested detail wrapper."""
    detail = exc.detail
    if isinstance(detail, dict):
        content = detail
    else:
        content = {
            "error": "http_error",
            "message": str(detail),
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return concise validation errors without echoing request bodies."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


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
        "docs": "/docs" if settings.api_docs_enabled else None,
        "health": "/health"
    }


# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(media_router)
app.include_router(processing_router)
app.include_router(search_router)
app.include_router(reports_router)
app.include_router(audit_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
