"""
EvidenceIQ Media Service
CRUD operations and business logic for media management.
"""
import os
from typing import List, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.config import settings
from app.media.models import MediaItem, MediaTag, ProcessingStatus
from app.users.models import User


def get_media_by_id(db: Session, media_id: str) -> Optional[MediaItem]:
    """Get media item by ID."""
    return db.query(MediaItem).filter(MediaItem.id == media_id).first()


def get_media_by_hash(db: Session, sha256_hash: str) -> Optional[MediaItem]:
    """Get media item by SHA256 hash (for deduplication)."""
    return db.query(MediaItem).filter(MediaItem.sha256_hash == sha256_hash).first()


def get_media_by_uuid(db: Session, uuid: str) -> Optional[MediaItem]:
    """Get media item by UUID."""
    return db.query(MediaItem).filter(MediaItem.uuid == uuid).first()


def list_media(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    mime_type: Optional[str] = None,
    classification: Optional[str] = None,
    processing_status: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    parent_id: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[List[MediaItem], int]:
    """
    List media items with optional filtering.
    
    Returns:
        Tuple of (items list, total count)
    """
    query = db.query(MediaItem)
    
    # Apply filters
    if mime_type:
        query = query.filter(MediaItem.mime_type == mime_type)
    
    if classification:
        query = query.filter(MediaItem.classification == classification)
    
    if processing_status:
        query = query.filter(MediaItem.processing_status == processing_status)
    
    if uploaded_by:
        query = query.filter(MediaItem.uploaded_by == uploaded_by)
    
    if parent_id:
        query = query.filter(MediaItem.parent_id == parent_id)
    elif parent_id is None:
        # By default, only show top-level items (not video frames/PDF pages)
        query = query.filter(MediaItem.parent_id.is_(None))
    
    if search:
        # Search in filename, description, or classification
        from sqlalchemy import or_
        search_filter = or_(
            MediaItem.original_filename.ilike(f"%{search}%"),
            MediaItem.description.ilike(f"%{search}%"),
            MediaItem.classification.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Get total count
    total = query.count()
    
    # Order by upload timestamp (newest first)
    query = query.order_by(desc(MediaItem.upload_timestamp))
    
    # Apply pagination
    items = query.offset(skip).limit(limit).all()
    
    return items, total


def create_media(db: Session, media_data: dict) -> MediaItem:
    """
    Create a new media item in the database.
    
    Args:
        db: Database session
        media_data: Dictionary with media data from ingest pipeline
    
    Returns:
        Created MediaItem
    """
    db_media = MediaItem(**media_data)
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media


def update_processing_status(
    db: Session,
    media_id: str,
    status: str,
    results: Optional[dict] = None
) -> Optional[MediaItem]:
    """Update processing status and optionally results."""
    media = get_media_by_id(db, media_id)
    if not media:
        return None
    
    media.processing_status = status
    
    if results:
        media.processing_results = results
        media.classification = results.get("classification")
        media.description = results.get("description")
        media.model_used = results.get("model_used")
        media.processed_at = func.now()
    
    db.commit()
    db.refresh(media)
    return media


def delete_media(db: Session, media_id: str, deleted_by: str) -> bool:
    """
    Delete a media item and its associated files.
    
    Args:
        db: Database session
        media_id: Media item ID
        deleted_by: User ID performing deletion
    
    Returns:
        True if deleted, False if not found
    """
    media = get_media_by_id(db, media_id)
    if not media:
        return False
    
    # Delete associated files
    storage_root = settings.resolved_storage_path
    
    # Delete original file
    original_path = storage_root / media.internal_path
    if original_path.exists():
        os.remove(original_path)
    
    # Delete redacted file if exists
    if media.redacted_path:
        redacted_path = storage_root / media.redacted_path
        if redacted_path.exists():
            os.remove(redacted_path)
    
    # Delete thumbnail if exists
    thumbnail_path = storage_root / "thumbnails" / f"{media.uuid}.jpg"
    if thumbnail_path.exists():
        os.remove(thumbnail_path)
    
    # Delete children (video frames, PDF pages)
    for child in media.children:
        child_path = storage_root / child.internal_path
        if child_path.exists():
            os.remove(child_path)
        db.delete(child)
    
    # Delete from database
    db.delete(media)
    db.commit()
    
    return True


def get_file_path(media: MediaItem, use_redacted: bool = False) -> Optional[Path]:
    """
    Get the file system path for a media item.
    
    Args:
        media: MediaItem
        use_redacted: If True, return redacted version path if available
    
    Returns:
        Path object or None if file doesn't exist
    """
    storage_root = settings.resolved_storage_path
    
    if use_redacted and media.redacted_path:
        path = storage_root / media.redacted_path
    else:
        path = storage_root / media.internal_path
    
    if path.exists():
        return path
    return None


def verify_file_integrity(media: MediaItem) -> bool:
    """
    Verify file integrity by comparing stored hash with actual file hash.
    
    Returns:
        True if file matches stored hash, False otherwise
    """
    from app.media.ingest import verify_file_hash
    
    path = get_file_path(media)
    if not path:
        return False
    
    return verify_file_hash(path, media.sha256_hash)


def get_user_media_stats(db: Session, user_id: str) -> dict:
    """Get media statistics for a user."""
    from sqlalchemy import func
    
    total = db.query(func.count(MediaItem.id)).filter(
        MediaItem.uploaded_by == user_id
    ).scalar()
    
    by_status = db.query(
        MediaItem.processing_status,
        func.count(MediaItem.id)
    ).filter(
        MediaItem.uploaded_by == user_id
    ).group_by(MediaItem.processing_status).all()
    
    by_type = db.query(
        MediaItem.mime_type,
        func.count(MediaItem.id)
    ).filter(
        MediaItem.uploaded_by == user_id
    ).group_by(MediaItem.mime_type).all()
    
    total_size = db.query(
        func.sum(MediaItem.file_size_bytes)
    ).filter(
        MediaItem.uploaded_by == user_id
    ).scalar()
    
    return {
        "total_files": total,
        "by_status": {status: count for status, count in by_status},
        "by_type": {mime: count for mime, count in by_type},
        "total_bytes": total_size or 0
    }


def get_media_children(db: Session, parent_id: str) -> List[MediaItem]:
    """Get child media items (video frames, PDF pages)."""
    return db.query(MediaItem).filter(
        MediaItem.parent_id == parent_id
    ).order_by(MediaItem.upload_timestamp).all()


def create_child_media(
    db: Session,
    parent_id: str,
    media_data: dict
) -> MediaItem:
    """
    Create a child media item (video frame or PDF page).
    
    Args:
        db: Database session
        parent_id: Parent media item ID
        media_data: Dictionary with child media data
    
    Returns:
        Created child MediaItem
    """
    media_data["parent_id"] = parent_id
    db_media = MediaItem(**media_data)
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media
