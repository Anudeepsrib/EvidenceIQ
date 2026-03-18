"""
EvidenceIQ Processing Router
Vision pipeline endpoints for single item and batch processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.auth.dependencies import get_current_user, require_permissions
from app.users.models import User
from app.media import service as media_service
from app.processing import service as processing_service
from app.processing.vision import list_available_models
from app.audit.service import log_action
from app.audit.models import AuditActionType

router = APIRouter(prefix="/process", tags=["Processing"])


@router.post("/{media_id}")
def process_single(
    media_id: str,
    request: Request,
    force: bool = False,
    model: Optional[str] = "llava",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"tag_classify"}))
):
    """
    Process a single media item through the vision pipeline.
    
    **Pipeline steps:**
    1. Classification (document | photograph | screenshot | ...)
    2. Description generation (2-3 factual sentences)
    3. Entity tagging (people, objects, location, etc.)
    4. CLIP embedding generation for semantic search
    
    **For videos:** Extracts frames at 1fps, processes each
    **For PDFs:** Extracts embedded images, processes each
    
    - **force**: Reprocess even if already processed (default: false)
    - **model**: Vision model - llava, bakllava, moondream (default: llava)
    """
    # Validate media exists
    media = media_service.get_media_by_id(db, media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    # Validate model
    if model not in ["llava", "bakllava", "moondream"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_model", "message": f"Model {model} not supported"}
        )
    
    # Process
    results = processing_service.process_single_media(
        db=db,
        media_id=media_id,
        model=model,
        force=force,
        processed_by=current_user.id
    )
    
    if "error" in results and not results.get("status"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "processing_failed", "message": results["error"]}
        )
    
    return results


@router.post("/batch")
def process_batch(
    request: Request,
    media_ids: list,
    force: bool = False,
    model: Optional[str] = "llava",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"tag_classify"}))
):
    """
    Process multiple media items in batch.
    
    Max 100 items per batch. Each item is processed sequentially.
    """
    if len(media_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "batch_too_large", "message": "Maximum 100 items per batch"}
        )
    
    if len(media_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_batch", "message": "No media IDs provided"}
        )
    
    # Validate model
    if model not in ["llava", "bakllava", "moondream"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "invalid_model", "message": f"Model {model} not supported"}
        )
    
    results = processing_service.batch_process(
        db=db,
        media_ids=media_ids,
        model=model,
        force=force,
        processed_by=current_user.id
    )
    
    # Log batch processing
    client_ip = getattr(request.state, "client_ip", None)
    log_action(
        db=db,
        action=AuditActionType.PROCESS,
        user_id=current_user.id,
        details={
            "batch_size": len(media_ids),
            "successful": results["successful"],
            "failed": results["failed"],
            "model_used": model
        },
        ip_address=client_ip
    )
    
    return results


@router.get("/models")
def list_models(
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    List available vision models in Ollama.
    """
    models = list_available_models()
    
    # Filter for vision models only
    vision_models = [m for m in models if any(
        v in m.lower() for v in ["llava", "bakllava", "moondream"]
    )]
    
    return {
        "available_models": vision_models,
        "default_model": "llava",
        "supported_models": ["llava", "bakllava", "moondream"]
    }


@router.get("/status/{media_id}")
def get_processing_status(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Get processing status for a media item.
    """
    media = media_service.get_media_by_id(db, media_id)
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "Media item not found"}
        )
    
    return {
        "media_id": media_id,
        "status": media.processing_status,
        "classification": media.classification,
        "model_used": media.model_used,
        "processed_at": media.processed_at,
        "description": media.description[:200] + "..." if media.description and len(media.description) > 200 else media.description
    }
