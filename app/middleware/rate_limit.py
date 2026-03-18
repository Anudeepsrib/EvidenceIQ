"""
EvidenceIQ Middleware - Rate Limiting
Rate limiting with SlowAPI.
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings

# Create rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests_per_minute}/minute"]
)


class RateLimitMiddleware:
    """
    Rate limiting configuration and error handling.
    
    Default: 60 requests per minute per IP address.
    Configurable via RATE_LIMIT_REQUESTS_PER_MINUTE env var.
    """
    
    @staticmethod
    def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        """Custom handler for rate limit exceeded."""
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please slow down."
            }
        )


def setup_rate_limiting(app):
    """
    Setup rate limiting on FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, RateLimitMiddleware.rate_limit_exceeded_handler)
    
    # Add limiter to middleware
    app.add_middleware(limiter.middleware_class)


# Decorator for custom rate limits on specific endpoints
def custom_rate_limit(limit_string: str):
    """
    Decorator to apply custom rate limits to specific endpoints.
    
    Usage:
        @router.post("/login")
        @custom_rate_limit("5/minute")
        def login(request: LoginRequest):
            ...
    """
    return limiter.limit(limit_string)
