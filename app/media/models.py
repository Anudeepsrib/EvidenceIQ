"""
EvidenceIQ Media Models
SQLAlchemy models for media items, tags, and processing status.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from app.database import Base
from app.users.models import UUID


class MediaItem(Base):
    """
    Media item model - images, videos, PDFs, and extracted frames/pages.
    
    Supports hierarchical structure (video frames, PDF pages as children).
    """
    __tablename__ = "media_items"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File identification
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    original_filename = Column(String(500), nullable=False)
    internal_path = Column(String(1000), nullable=False)  # Relative to storage root
    
    # File metadata
    mime_type = Column(String(100), nullable=False, index=True)
    file_size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Dimensions (for images/videos)
    width_px = Column(Integer, nullable=True)
    height_px = Column(Integer, nullable=True)
    duration_seconds = Column(Float, nullable=True)  # For videos
    
    # Hierarchy (for video frames, PDF pages)
    parent_id = Column(UUID, ForeignKey("media_items.id"), nullable=True, index=True)
    
    # Ownership
    uploaded_by = Column(UUID, ForeignKey("users.id"), nullable=False, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Processing status
    processing_status = Column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )  # pending | processing | ready | failed
    
    # EXIF metadata (JSON, scrubbed of PII)
    exif_metadata = Column(JSON, nullable=True)
    
    # PII flags (JSON indicating what was scrubbed)
    pii_flags = Column(JSON, nullable=True)
    
    # Processing results
    classification = Column(String(50), nullable=True)  # document | photograph | screenshot | ...
    description = Column(Text, nullable=True)
    processing_results = Column(JSON, nullable=True)  # Full vision model output
    model_used = Column(String(50), nullable=True)  # llava | bakllava | moondream
    processed_at = Column(DateTime, nullable=True)
    
    # Redaction tracking
    redacted_path = Column(String(1000), nullable=True)  # Path to redacted copy
    redacted_at = Column(DateTime, nullable=True)
    redacted_by = Column(UUID, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    redactor = relationship("User", foreign_keys=[redacted_by])
    parent = relationship("MediaItem", remote_side=[id], backref="children")
    tags = relationship("MediaTag", back_populates="media_item", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MediaItem(id={self.id}, filename={self.original_filename}, status={self.processing_status})>"


class MediaTag(Base):
    """
    Tag/label for media items extracted by vision models.
    Separate table for flexible querying.
    """
    __tablename__ = "media_tags"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = Column(UUID, ForeignKey("media_items.id"), nullable=False, index=True)
    tag_type = Column(String(50), nullable=False, index=True)  # object | scene | concept | custom
    tag_value = Column(String(200), nullable=False, index=True)
    confidence = Column(Float, nullable=True)  # Model confidence if available
    
    # Relationship
    media_item = relationship("MediaItem", back_populates="tags")
    
    def __repr__(self):
        return f"<MediaTag(media_id={self.media_id}, type={self.tag_type}, value={self.tag_value})>"


class ProcessingStatus:
    """Processing status constants."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class MediaClassification:
    """Media classification constants from vision models."""
    DOCUMENT = "document"
    PHOTOGRAPH = "photograph"
    SCREENSHOT = "screenshot"
    DIAGRAM = "diagram"
    SURVEILLANCE_STILL = "surveillance_still"
    MEDICAL_IMAGE = "medical_image"
    CHART = "chart"
    MIXED = "mixed"
    UNKNOWN = "unknown"
