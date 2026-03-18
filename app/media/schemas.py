"""
EvidenceIQ Media Schemas
Pydantic models for media request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class MediaUploadResponse(BaseModel):
    """Response after media upload."""
    id: str
    uuid: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    processing_status: str
    upload_timestamp: datetime
    message: str = "Upload successful"


class MediaItemResponse(BaseModel):
    """Full media item response."""
    id: str
    uuid: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    duration_seconds: Optional[float] = None
    parent_id: Optional[str] = None
    uploaded_by: str
    upload_timestamp: datetime
    processing_status: str
    classification: Optional[str] = None
    description: Optional[str] = None
    exif_metadata: Optional[Dict[str, Any]] = None
    pii_flags: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None
    processed_at: Optional[datetime] = None
    redacted_at: Optional[datetime] = None
    children_count: Optional[int] = None

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """Response for listing media items."""
    items: List[MediaItemResponse]
    total: int
    page: int
    page_size: int


class MediaSearchParams(BaseModel):
    """Query parameters for media search."""
    mime_type: Optional[str] = None
    classification: Optional[str] = None
    processing_status: Optional[str] = None
    uploaded_by: Optional[str] = None
    parent_id: Optional[str] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class ProcessingRequest(BaseModel):
    """Request to process a media item."""
    force: bool = Field(False, description="Reprocess even if already processed")
    model: str = Field("llava", pattern="^(llava|bakllava|moondream)$")


class ProcessingResponse(BaseModel):
    """Response after processing request."""
    media_id: str
    status: str
    message: str


class BatchProcessingRequest(BaseModel):
    """Request to process multiple media items."""
    media_ids: List[str] = Field(..., min_length=1, max_length=100)
    force: bool = Field(False)
    model: str = Field("llava", pattern="^(llava|bakllava|moondream)$")


class RedactionRequest(BaseModel):
    """Request to redact PII from media metadata."""
    scrub_gps: bool = Field(True, description="Remove GPS coordinates")
    scrub_camera_serial: bool = Field(True, description="Remove camera serial numbers")
    scrub_owner: bool = Field(True, description="Remove owner/artist fields")
    scrub_software: bool = Field(True, description="Remove software version (fingerprinting)")
    scrub_dates: bool = Field(False, description="Remove date fields (configurable)")


class RedactionResponse(BaseModel):
    """Response after redaction."""
    media_id: str
    original_hash: str
    redacted_hash: str
    redacted_path: str
    scrubbed_fields: List[str]
    message: str = "Redaction complete"


class TagResponse(BaseModel):
    """Media tag response."""
    id: str
    tag_type: str
    tag_value: str
    confidence: Optional[float] = None


class FileStreamResponse(BaseModel):
    """File streaming response metadata."""
    media_id: str
    filename: str
    mime_type: str
    size_bytes: int
    hash_verified: bool
