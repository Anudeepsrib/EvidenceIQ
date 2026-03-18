"""
EvidenceIQ Processing - Service
Orchestrate vision pipeline: classify, describe, tag, embed.
"""
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from app.config import settings
from app.media import service as media_service
from app.media.models import MediaItem, ProcessingStatus
from app.processing.vision import process_image_full
from app.processing.embeddings import store_embedding
from app.processing.frames import extract_video_frames, get_video_info
from app.processing.extractor import extract_images_from_pdf, get_pdf_info
from app.audit.service import log_action
from app.audit.models import AuditActionType


def process_single_media(
    db: Session,
    media_id: str,
    model: str = None,
    force: bool = False,
    processed_by: str = None
) -> Dict[str, Any]:
    """
    Process a single media item through the full vision pipeline.
    
    Args:
        db: Database session
        media_id: Media item ID
        model: Vision model to use (default: from settings)
        force: Reprocess even if already processed
        processed_by: User ID performing the processing
    
    Returns:
        Processing results dict
    """
    if model is None:
        model = settings.vision_model_default
    
    # Get media item
    media = media_service.get_media_by_id(db, media_id)
    if not media:
        return {"error": "Media not found", "media_id": media_id}
    
    # Check if already processed (unless force=True)
    if media.processing_status == ProcessingStatus.READY and not force:
        return {
            "media_id": media_id,
            "status": "skipped",
            "message": "Already processed. Use force=True to reprocess."
        }
    
    # Update status to processing
    media_service.update_processing_status(db, media_id, ProcessingStatus.PROCESSING)
    
    # Get file path
    storage_root = settings.resolved_storage_path
    file_path = storage_root / media.internal_path
    
    if not file_path.exists():
        media_service.update_processing_status(db, media_id, ProcessingStatus.FAILED)
        return {"error": "File not found", "media_id": media_id}
    
    results = {
        "media_id": media_id,
        "model_used": model,
        "steps": []
    }
    
    try:
        # Handle video: extract frames first
        if media.mime_type.startswith('video/'):
            frame_results = _process_video(db, media, file_path, storage_root, model, processed_by)
            results["video_processing"] = frame_results
        
        # Handle PDF: extract images first
        elif media.mime_type == 'application/pdf':
            pdf_results = _process_pdf(db, media, file_path, storage_root, model, processed_by)
            results["pdf_processing"] = pdf_results
        
        # Handle image: process directly
        elif media.mime_type.startswith('image/'):
            image_results = _process_image(db, media, str(file_path), model)
            results["image_processing"] = image_results
        
        else:
            results["error"] = f"Unsupported MIME type: {media.mime_type}"
            media_service.update_processing_status(db, media_id, ProcessingStatus.FAILED)
            return results
        
        # Mark as ready
        media_service.update_processing_status(
            db, media_id, 
            ProcessingStatus.READY,
            results={"full_results": results, "model_used": model}
        )
        
        # Log processing
        log_action(
            db=db,
            action=AuditActionType.PROCESS,
            user_id=processed_by,
            resource_type="media",
            resource_id=media_id,
            details={
                "model_used": model,
                "classification": results.get("image_processing", {}).get("classification"),
                "steps_completed": len(results.get("steps", []))
            }
        )
        
        results["status"] = "success"
        return results
        
    except Exception as e:
        # Mark as failed
        media_service.update_processing_status(db, media_id, ProcessingStatus.FAILED)
        
        return {
            "error": str(e),
            "media_id": media_id,
            "status": "failed"
        }


def _process_image(db: Session, media: MediaItem, file_path: str, model: str) -> Dict[str, Any]:
    """Process a single image through vision pipeline."""
    # Step 1: Vision processing
    vision_results = process_image_full(file_path, model)
    
    # Update media with results
    if vision_results["success"]:
        media.classification = vision_results["classification"]
        media.description = vision_results["description"]
        media.model_used = model
        db.commit()
    
    # Step 2: Generate and store embedding
    metadata = {
        "classification": vision_results.get("classification", "unknown"),
        "description": vision_results.get("description", ""),
        "tags": vision_results.get("tags", {}),
        "uploaded_by": media.uploaded_by,
        "upload_date": media.upload_timestamp.isoformat() if media.upload_timestamp else ""
    }
    
    embedding_stored = store_embedding(str(media.id), file_path, metadata)
    
    return {
        "vision_results": vision_results,
        "embedding_stored": embedding_stored
    }


def _process_video(
    db: Session, 
    media: MediaItem, 
    file_path: Path, 
    storage_root: Path,
    model: str,
    processed_by: str
) -> Dict[str, Any]:
    """Process video by extracting frames and processing them."""
    # Get video info
    video_info = get_video_info(str(file_path))
    
    # Update media with duration
    if video_info.get("duration_seconds"):
        media.duration_seconds = video_info["duration_seconds"]
        db.commit()
    
    # Extract frames
    frames = extract_video_frames(str(file_path))
    
    # Process each frame
    processed_frames = []
    for frame_data in frames:
        # Create child media record
        frame_path = storage_root / frame_data["extracted_path"]
        
        # Compute hash for frame
        import hashlib
        with open(frame_path, 'rb') as f:
            frame_hash = hashlib.sha256(f.read()).hexdigest()
        frame_data["sha256_hash"] = frame_hash
        frame_data["uploaded_by"] = media.uploaded_by
        frame_data["parent_id"] = media.id
        frame_data["processing_status"] = "pending"
        frame_data["original_filename"] = f"{media.original_filename}_frame_{frame_data['frame_number']}"
        
        # Create child media
        child_media = media_service.create_child_media(db, str(media.id), frame_data)
        
        # Process frame
        frame_results = _process_image(db, child_media, str(frame_path), model)
        processed_frames.append({
            "frame_id": str(child_media.id),
            "results": frame_results
        })
    
    # Classify parent based on frames (use most common classification)
    classifications = [f["results"]["vision_results"].get("classification") for f in processed_frames]
    if classifications:
        from collections import Counter
        most_common = Counter([c for c in classifications if c]).most_common(1)
        if most_common:
            media.classification = most_common[0][0]
            db.commit()
    
    return {
        "frames_extracted": len(frames),
        "frames_processed": len(processed_frames),
        "video_info": video_info
    }


def _process_pdf(
    db: Session,
    media: MediaItem,
    file_path: Path,
    storage_root: Path,
    model: str,
    processed_by: str
) -> Dict[str, Any]:
    """Process PDF by extracting images and processing them."""
    # Get PDF info
    pdf_info = get_pdf_info(str(file_path))
    
    # Extract images
    images = extract_images_from_pdf(str(file_path))
    
    # Process each image
    processed_images = []
    for img_data in images:
        # Create child media record
        img_path = storage_root / img_data["extracted_path"]
        
        img_data["uploaded_by"] = media.uploaded_by
        img_data["parent_id"] = media.id
        img_data["processing_status"] = "pending"
        img_data["original_filename"] = f"{media.original_filename}_img_{img_data['page_number']}"
        
        # Create child media
        child_media = media_service.create_child_media(db, str(media.id), img_data)
        
        # Process image
        img_results = _process_image(db, child_media, str(img_path), model)
        processed_images.append({
            "image_id": str(child_media.id),
            "results": img_results
        })
    
    # Classify parent
    if processed_images:
        media.classification = "document"
        db.commit()
    
    return {
        "images_extracted": len(images),
        "images_processed": len(processed_images),
        "pdf_info": pdf_info
    }


def batch_process(
    db: Session,
    media_ids: list,
    model: str = None,
    force: bool = False,
    processed_by: str = None
) -> Dict[str, Any]:
    """
    Process multiple media items in batch.
    
    Returns:
        Dict with results for each media item
    """
    results = {
        "total": len(media_ids),
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }
    
    for media_id in media_ids:
        result = process_single_media(db, media_id, model, force, processed_by)
        
        if result.get("status") == "success":
            results["successful"] += 1
        elif result.get("status") == "skipped":
            results["skipped"] += 1
        else:
            results["failed"] += 1
        
        results["details"].append(result)
    
    return results
