"""
EvidenceIQ Reports Service
Generate evidence reports with chain of custody documentation.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from io import BytesIO

from app.media import service as media_service
from app.reports.builder import build_evidence_report
from app.audit.service import log_action
from app.audit.models import AuditActionType


class ReportIntegrityError(RuntimeError):
    """Raised when report generation detects modified or missing evidence."""

    def __init__(self, media_id: str):
        super().__init__(f"File integrity check failed for media {media_id}")
        self.media_id = media_id


def generate_evidence_report(
    db: Session,
    media_ids: List[str],
    case_name: Optional[str] = None,
    notes: Dict[str, str] = None,
    generated_by: str = None,
    generated_by_name: str = None
) -> BytesIO:
    """
    Generate an evidence report PDF.
    
    Args:
        db: Database session
        media_ids: List of media item IDs to include
        case_name: Optional case name for the report
        notes: Optional dict of notes per media_id
        generated_by: User ID who generated the report
        generated_by_name: Username who generated the report
    
    Returns:
        BytesIO buffer with PDF content
    """
    # Collect media item data
    media_items = []
    
    for media_id in media_ids:
        media = media_service.get_media_by_id(db, media_id)
        
        if not media:
            continue

        if not media_service.verify_file_integrity(media):
            raise ReportIntegrityError(str(media_id))
        
        # Get thumbnail path
        from app.config import settings
        thumbnail_path = str(settings.resolved_storage_path / "thumbnails" / f"{media.uuid}_256.jpg")
        if not settings.resolved_storage_path.joinpath("thumbnails", f"{media.uuid}_256.jpg").exists():
            thumbnail_path = None
        
        # Build item data
        item_data = {
            "id": str(media.id),
            "uuid": media.uuid,
            "original_filename": media.original_filename,
            "mime_type": media.mime_type,
            "file_size_bytes": media.file_size_bytes,
            "sha256_hash": media.sha256_hash,
            "classification": media.classification,
            "description": media.description,
            "model_used": media.model_used,
            "upload_timestamp": media.upload_timestamp,
            "width_px": media.width_px,
            "height_px": media.height_px,
            "thumbnail_path": thumbnail_path,
            "redaction_status": "Redacted" if media.redacted_at else "Not redacted",
            "hash_verified": True,
            "audit_trail_ref": f"media:{media.id}",
        }
        
        media_items.append(item_data)
    
    # Generate PDF
    pdf_buffer = build_evidence_report(
        case_name=case_name or "Evidence Report",
        generated_by=f"{generated_by_name or 'Unknown'} ({generated_by or 'unknown-id'})",
        media_items=media_items,
        notes=notes
    )
    
    # Log report generation
    log_action(
        db=db,
        action=AuditActionType.EXPORT,
        user_id=generated_by,
        details={
            "case_name": case_name,
            "media_count": len(media_ids),
            "included_media": media_ids,
            "export_type": "pdf_report",
        }
    )
    
    return pdf_buffer


def get_report_metadata(
    db: Session,
    media_ids: List[str],
    case_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get metadata about a potential report (without generating PDF).
    
    Returns summary statistics.
    """
    media_items = []
    total_size = 0
    classifications = {}
    
    for media_id in media_ids:
        media = media_service.get_media_by_id(db, media_id)
        
        if not media:
            continue
        
        media_items.append(media)
        total_size += media.file_size_bytes
        
        cls = media.classification or "unknown"
        classifications[cls] = classifications.get(cls, 0) + 1
    
    return {
        "case_name": case_name,
        "total_items": len(media_items),
        "total_size_mb": round(total_size / 1024 / 1024, 2),
        "classifications": classifications,
        "valid_items": len(media_items),
        "invalid_items": len(media_ids) - len(media_items)
    }
