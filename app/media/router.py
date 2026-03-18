"""
EvidenceIQ Media Router
Upload, list, get, file streaming, and redaction endpoints.
"""
import os
from typing import Optional
from pathlib import Path
from datetime import datetime

from fastapi import (
    APIRouter, Depends, HTTPException, status,
    UploadFile, File, Form, Query, Request
)
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
import aiofiles

from app.database import get_db
from app.config import settings
from app.auth.dependencies import get_current_user, require_permissions, require_roles
from app.users.models import User
from app.media import service as media_service
from app.media import ingest as ingest_pipeline
from app.media.schemas import (
    MediaUploadResponse, MediaItemResponse, MediaListResponse,
    MediaSearchParams, RedactionRequest, RedactionResponse,
    ProcessingRequest
)
from app.audit.service import log_action
from app.audit.models import AuditActionType

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    request: Request,
    file: UploadFile = File(..., description="Media file to upload (max 500MB)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"upload_media"}))
):
    """
    Upload a media file (image, video, or PDF).
    
    **Accepted types:** JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, PDF
    
    **Processing:**
    - MIME type validation via python-magic
    - Filename sanitization (path traversal protection)
    - SHA256 hash computation
    - EXIF metadata extraction
    - PII flagging
    - UUID-based internal storage
    
    Returns upload metadata. Processing happens asynchronously via `/process/{id}`.
    """
    # Validate file size (stream to check)
    contents = await file.read()
    
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "file_too_large",
                "message": f"File exceeds {settings.max_file_size_mb}MB limit"
            }
        )
    
    try:
        # Run ingest pipeline
        media_data = ingest_pipeline.process_upload(
            filename=file.filename,
            file_content=contents,
            uploader_id=current_user.id
        )
        
        # Check for duplicate by hash
        existing = media_service.get_media_by_hash(db, media_data["sha256_hash"])
        if existing:
            # Return existing media info
            return MediaUploadResponse(
                id=str(existing.id),
                uuid=existing.uuid,
                original_filename=existing.original_filename,
                mime_type=existing.mime_type,
                file_size_bytes=existing.file_size_bytes,
                sha256_hash=existing.sha256_hash,
                processing_status=existing.processing_status,
                upload_timestamp=existing.upload_timestamp,
                message="File already exists (duplicate detected)"
            )
        
        # Create database record
        media = media_service.create_media(db, media_data)
        
        # Log upload
        client_ip = getattr(request.state, "client_ip", None)
        log_action(
            db=db,
            action=AuditActionType.UPLOAD,
            user_id=current_user.id,
            resource_type="media",
            resource_id=media.id,
            details={
                "filename": media.original_filename,
                "mime_type": media.mime_type,
                "size_bytes": media.file_size_bytes,
                "sha256": media.sha256_hash
            },
            ip_address=client_ip
        )
        
        return MediaUploadResponse(
            id=str(media.id),
            uuid=media.uuid,
            original_filename=media.original_filename,
            mime_type=media.mime_type,
            file_size_bytes=media.file_size_bytes,
            sha256_hash=media.sha256_hash,
            processing_status=media.processing_status,
            upload_timestamp=media.upload_timestamp
        )
        
    except ingest_pipeline.IngestError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE if e.code == "unsupported_type" 
            else status.HTTP_400_BAD_REQUEST,
            detail={"error": e.code, "message": e.message}
        )


@router.get("", response_model=MediaListResponse)
def list_media(
    mime_type: Optional[str] = Query(None, description="Filter by MIME type"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    processing_status: Optional[str] = Query(None, pattern="^(pending|processing|ready|failed)$"),
    search: Optional[str] = Query(None, description="Search in filename/description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    List media items with filtering and pagination.
    
    By default, shows only top-level items (not video frames/PDF pages).
    """
    skip = (page - 1) * page_size
    
    items, total = media_service.list_media(
        db,
        skip=skip,
        limit=page_size,
        mime_type=mime_type,
        classification=classification,
        processing_status=processing_status,
        search=search
    )
    
    # Get children count for each item
    result_items = []
    for item in items:
        item_dict = {
            **{k: v for k, v in item.__dict__.items() if not k.startswith('_')},
            "children_count": len(item.children) if item.children else 0
        }
        result_items.append(item_dict)
    
    return MediaListResponse(
        items=result_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{media_id}", response_model=MediaItemResponse)
def get_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Get detailed information about a specific media item.
    
    Includes metadata, processing status, and child items count.
    """
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Add children count
    result = {
        **{k: v for k, v in media.__dict__.items() if not k.startswith('_')},
        "children_count": len(media.children) if media.children else 0
    }
    
    return result


@router.get("/{media_id}/file")
def get_media_file(
    media_id: str,
    use_redacted: bool = Query(False, description="Serve redacted version if available"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Stream the media file (original or redacted version).
    
    **Security:**
    - Authenticated access only
    - SHA256 hash verified on every access
    - Returns 410 Gone if file integrity check fails (tampering detected)
    
    Note: Files are never served directly from storage; always through this endpoint.
    """
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Get file path
    file_path = media_service.get_file_path(media, use_redacted=use_redacted)
    
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "file_not_found", "message": "File not found on storage"}
        )
    
    # Verify file integrity (chain of custody check)
    if not media_service.verify_file_integrity(media):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail={
                "error": "integrity_check_failed",
                "message": "File integrity check failed. File may have been tampered with."
            }
        )
    
    # Determine filename for download
    filename = media.original_filename
    if use_redacted:
        name_part = Path(filename).stem
        ext = Path(filename).suffix
        filename = f"{name_part}_redacted{ext}"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media.mime_type
    )


@router.get("/{media_id}/thumbnail")
def get_media_thumbnail(
    media_id: str,
    size: int = Query(256, ge=64, le=1024, description="Thumbnail size in pixels"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Get or generate a thumbnail for the media item.
    
    Thumbnails are generated on first request and cached.
    """
    from PIL import Image
    import io
    
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Check for cached thumbnail
    thumb_path = settings.resolved_storage_path / "thumbnails" / f"{media.uuid}_{size}.jpg"
    
    if thumb_path.exists():
        return FileResponse(path=str(thumb_path), media_type="image/jpeg")
    
    # Generate thumbnail
    file_path = media_service.get_file_path(media)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "file_not_found", "message": "Original file not found"}
        )
    
    try:
        with Image.open(file_path) as img:
            # Convert to RGB for JPEG
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize maintaining aspect ratio
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb_path, "JPEG", quality=85)
            
            return FileResponse(path=str(thumb_path), media_type="image/jpeg")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "thumbnail_error", "message": str(e)}
        )


@router.delete("/{media_id}", status_code=status.HTTP_200_OK)
def delete_media(
    media_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"delete_media"}))
):
    """
    Delete a media item and all associated files (admin only).
    
    **Warning:** This permanently deletes:
    - Original file
    - Redacted copy (if exists)
    - Thumbnails
    - Video frames / PDF pages (children)
    - Database record
    
    Action is logged to audit table.
    """
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Delete
    success = media_service.delete_media(db, media_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "delete_failed", "message": "Failed to delete media"}
        )
    
    # Log deletion
    client_ip = getattr(request.state, "client_ip", None)
    log_action(
        db=db,
        action=AuditActionType.DELETE,
        user_id=current_user.id,
        resource_type="media",
        resource_id=media_id,
        details={
            "filename": media.original_filename,
            "sha256": media.sha256_hash
        },
        ip_address=client_ip
    )
    
    return {"message": "Media item deleted successfully"}


@router.post("/{media_id}/redact", response_model=RedactionResponse)
def redact_media(
    media_id: str,
    request: Request,
    redact_request: RedactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"redact_metadata"}))
):
    """
    Redact PII from media EXIF metadata (investigator and admin only).
    
    **Scrubbed fields (configurable):**
    - GPS coordinates (flagged but not auto-deleted)
    - Camera serial numbers
    - Owner/artist fields
    - Software version (fingerprinting risk)
    - Date fields (optional)
    
    **Important:** Original file is never modified. A new redacted copy is created.
    """
    from app.processing.metadata import scrub_exif_metadata
    
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Only images have EXIF
    if not media.mime_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "not_applicable", "message": "Redaction only applicable to images"}
        )
    
    # Get original file path
    file_path = media_service.get_file_path(media)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "file_not_found", "message": "Original file not found"}
        )
    
    # Generate redacted file path
    redacted_path = settings.resolved_storage_path / "redacted" / f"{media.uuid}_redacted.jpg"
    redacted_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Perform redaction
        scrubbed_fields = scrub_exif_metadata(
            str(file_path),
            str(redacted_path),
            scrub_gps=redact_request.scrub_gps,
            scrub_camera_serial=redact_request.scrub_camera_serial,
            scrub_owner=redact_request.scrub_owner,
            scrub_software=redact_request.scrub_software,
            scrub_dates=redact_request.scrub_dates
        )
        
        # Compute new hash
        import hashlib
        with open(redacted_path, 'rb') as f:
            redacted_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Update database
        media.redacted_path = str(redacted_path.relative_to(settings.resolved_storage_path))
        media.redacted_at = datetime.utcnow()
        media.redacted_by = current_user.id
        
        # Update PII flags
        media.pii_flags = {
            "scrubbed_at": datetime.utcnow().isoformat(),
            "scrubbed_by": str(current_user.id),
            "scrubbed_fields": scrubbed_fields
        }
        
        db.commit()
        
        # Log redaction
        client_ip = getattr(request.state, "client_ip", None)
        log_action(
            db=db,
            action=AuditActionType.REDACT,
            user_id=current_user.id,
            resource_type="media",
            resource_id=media_id,
            details={
                "scrubbed_fields": scrubbed_fields,
                "original_hash": media.sha256_hash,
                "redacted_hash": redacted_hash
            },
            ip_address=client_ip
        )
        
        return RedactionResponse(
            media_id=media_id,
            original_hash=media.sha256_hash,
            redacted_hash=redacted_hash,
            redacted_path=str(media.redacted_path),
            scrubbed_fields=scrubbed_fields
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "redaction_failed", "message": str(e)}
        )


@router.get("/{media_id}/children", response_model=list[MediaItemResponse])
def get_media_children(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Get child media items (video frames, PDF pages) for a parent item.
    """
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    children = media_service.get_media_children(db, media_id)
    
    return [
        {k: v for k, v in child.__dict__.items() if not k.startswith('_')}
        for child in children
    ]
