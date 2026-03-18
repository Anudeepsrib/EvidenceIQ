# EvidenceIQ Dockerfile
# Production-grade Python 3.11 image with security hardening

FROM python:3.11-slim-bookworm

# Security: Run as non-root user
RUN groupadd -r evidenceiq && useradd -r -g evidenceiq evidenceiq

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create storage directories with proper permissions
RUN mkdir -p /app/storage/uploads /app/storage/redacted /app/storage/thumbnails /app/storage/reports \
    && chown -R evidenceiq:evidenceiq /app

# Switch to non-root user
USER evidenceiq

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
