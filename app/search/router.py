"""
EvidenceIQ Search Router
Semantic, tag, and metadata search endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_permissions
from app.users.models import User
from app.search import service as search_service
from app.audit.service import log_action
from app.audit.models import AuditActionType

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/semantic")
def semantic_search(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Semantic search using natural language queries.
    
    Examples:
    - "photos with people outdoors at night"
    - "documents containing charts"
    - "medical images with X-rays"
    
    Uses CLIP embeddings for semantic similarity matching.
    """
    # Hash the query for audit logging (privacy)
    import hashlib
    query_hash = hashlib.sha256(q.encode()).hexdigest()[:16]
    
    # Build filters
    filters = {}
    if classification:
        filters["classification"] = classification
    
    # Perform search
    results = search_service.search_semantic(q, top_k, filters)
    
    # Log search (hashed query for privacy)
    client_ip = getattr(request.state, "client_ip", None)
    log_action(
        db=db,
        action=AuditActionType.SEARCH,
        user_id=current_user.id,
        details={
            "query_hash": query_hash,
            "result_count": len(results),
            "search_type": "semantic"
        },
        ip_address=client_ip
    )
    
    return {
        "query": q,
        "results": results,
        "total": len(results)
    }


@router.get("/tags")
def tag_search(
    request: Request,
    tags: List[str] = Query(..., description="Tag values to search for"),
    tag_type: Optional[str] = Query(None, description="Filter by tag type"),
    match_all: bool = Query(False, description="Match all tags (AND) vs any (OR)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Search media by tags extracted by vision models.
    
    Tags include: objects, scene descriptions, content types.
    """
    skip = (page - 1) * page_size
    
    items, total = search_service.search_by_tags(
        db, tags, tag_type, match_all, skip, page_size
    )
    
    # Log search
    client_ip = getattr(request.state, "client_ip", None)
    log_action(
        db=db,
        action=AuditActionType.SEARCH,
        user_id=current_user.id,
        details={
            "tags": tags,
            "result_count": len(items),
            "search_type": "tag"
        },
        ip_address=client_ip
    )
    
    return {
        "tags": tags,
        "match_all": match_all,
        "items": [
            {
                "id": str(item.id),
                "uuid": item.uuid,
                "filename": item.original_filename,
                "classification": item.classification,
                "description": item.description[:200] + "..." if item.description and len(item.description) > 200 else item.description,
                "upload_timestamp": item.upload_timestamp
            }
            for item in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/combined")
def combined_search(
    request: Request,
    q: Optional[str] = Query(None, description="Semantic search query"),
    tags: Optional[List[str]] = Query(None, description="Tag filters"),
    classification: Optional[str] = Query(None, description="Classification filter"),
    mime_type: Optional[str] = Query(None, description="MIME type filter"),
    date_from: Optional[str] = Query(None, description="Date from (ISO format)"),
    date_to: Optional[str] = Query(None, description="Date to (ISO format)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Combined search: semantic + tags + metadata filters.
    
    Results are scored and ranked by relevance across all methods.
    """
    skip = (page - 1) * page_size
    
    results = search_service.combined_search(
        db=db,
        query_text=q,
        tags=tags,
        classification=classification,
        mime_type=mime_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=page_size
    )
    
    # Format response
    formatted_items = []
    for item in results["combined"]:
        media = item["media_item"]
        formatted_items.append({
            "media_id": item["media_id"],
            "score": item["score"],
            "matches": item["matches"],
            "uuid": media.uuid,
            "filename": media.original_filename,
            "classification": media.classification,
            "description": media.description[:200] + "..." if media.description and len(media.description) > 200 else media.description,
            "mime_type": media.mime_type,
            "upload_timestamp": media.upload_timestamp
        })
    
    # Log search
    client_ip = getattr(request.state, "client_ip", None)
    import hashlib
    query_hash = hashlib.sha256((q or "").encode()).hexdigest()[:16]
    
    log_action(
        db=db,
        action=AuditActionType.SEARCH,
        user_id=current_user.id,
        details={
            "query_hash": query_hash,
            "result_count": results["total"],
            "search_type": "combined"
        },
        ip_address=client_ip
    )
    
    return {
        "query": q,
        "filters": {
            "tags": tags,
            "classification": classification,
            "mime_type": mime_type,
            "date_from": date_from,
            "date_to": date_to
        },
        "items": formatted_items,
        "total": results["total"],
        "page": page,
        "page_size": page_size
    }


@router.get("/suggestions")
def search_suggestions(
    partial: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions({"view_search"}))
):
    """
    Get autocomplete suggestions for search.
    
    Returns matching tags, classifications, and filenames.
    """
    suggestions = search_service.get_search_suggestions(db, partial, limit)
    
    return {
        "partial": partial,
        "suggestions": suggestions,
        "count": len(suggestions)
    }
