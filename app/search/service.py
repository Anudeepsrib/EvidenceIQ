"""
EvidenceIQ Search Service
ChromaDB semantic search + SQL tag search.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_

from app.processing.embeddings import semantic_search as embedding_search
from app.media.models import MediaItem, MediaTag


def search_by_tags(
    db: Session,
    tags: List[str],
    tag_type: Optional[str] = None,
    match_all: bool = False,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[MediaItem], int]:
    """
    Search media by tags.
    
    Args:
        db: Database session
        tags: List of tag values to search for
        tag_type: Optional tag type filter
        match_all: If True, media must have ALL tags; if False, ANY tag
        skip: Pagination offset
        limit: Pagination limit
    
    Returns:
        Tuple of (media items, total count)
    """
    if not tags:
        return [], 0
    
    # Build query
    query = db.query(MediaItem).join(MediaTag)
    
    # Tag value filter
    if match_all:
        # Must have all tags
        for tag in tags:
            query = query.filter(MediaTag.tag_value.ilike(f"%{tag}%"))
    else:
        # Can have any tag
        tag_filter = or_(*[MediaTag.tag_value.ilike(f"%{tag}%") for tag in tags])
        query = query.filter(tag_filter)
    
    if tag_type:
        query = query.filter(MediaTag.tag_type == tag_type)
    
    # Only show processed items with tags
    query = query.filter(MediaItem.processing_status == "ready")
    
    # Distinct media items
    query = query.distinct()
    
    # Get total
    total = query.count()
    
    # Order and paginate
    query = query.order_by(desc(MediaItem.upload_timestamp))
    items = query.offset(skip).limit(limit).all()
    
    return items, total


def search_semantic(
    query_text: str,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Semantic search using CLIP embeddings.
    
    Args:
        query_text: Natural language query
        top_k: Number of results
        filters: Optional metadata filters
    
    Returns:
        List of search results
    """
    return embedding_search(query_text, top_k, filters)


def combined_search(
    db: Session,
    query_text: Optional[str] = None,
    tags: Optional[List[str]] = None,
    classification: Optional[str] = None,
    mime_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Combined search: semantic + tags + metadata filters.
    
    Returns ranked results from multiple search methods.
    """
    results = {
        "semantic_results": [],
        "tag_results": [],
        "metadata_results": [],
        "combined": [],
        "total": 0
    }
    
    media_ids = set()
    scored_results = {}
    
    # 1. Semantic search (if query text provided)
    if query_text:
        filters = {}
        if classification:
            filters["classification"] = classification
        
        semantic_results = search_semantic(query_text, top_k=limit * 2, filters=filters)
        results["semantic_results"] = semantic_results
        
        for r in semantic_results:
            media_ids.add(r["media_id"])
            scored_results[r["media_id"]] = {
                "score": r["score"] * 1.0,  # Semantic score weight
                "semantic_score": r["score"],
                "metadata": r["metadata"]
            }
    
    # 2. Tag search (if tags provided)
    if tags:
        tag_items, tag_total = search_by_tags(db, tags, skip=skip, limit=limit)
        results["tag_results"] = [{"id": str(i.id), "type": "tag_match"} for i in tag_items]
        
        for item in tag_items:
            item_id = str(item.id)
            media_ids.add(item_id)
            
            if item_id in scored_results:
                scored_results[item_id]["score"] += 0.5  # Tag match bonus
                scored_results[item_id]["tag_match"] = True
            else:
                scored_results[item_id] = {
                    "score": 0.5,
                    "tag_match": True,
                    "media_item": item
                }
    
    # 3. Metadata search
    query = db.query(MediaItem)
    
    if classification:
        query = query.filter(MediaItem.classification == classification)
    
    if mime_type:
        query = query.filter(MediaItem.mime_type == mime_type)
    
    if date_from:
        from datetime import datetime
        query = query.filter(MediaItem.upload_timestamp >= datetime.fromisoformat(date_from))
    
    if date_to:
        from datetime import datetime
        query = query.filter(MediaItem.upload_timestamp <= datetime.fromisoformat(date_to))
    
    # Only processed items
    query = query.filter(MediaItem.processing_status == "ready")
    
    metadata_items = query.all()
    results["metadata_results"] = [{"id": str(i.id), "type": "metadata_match"} for i in metadata_items]
    
    for item in metadata_items:
        item_id = str(item.id)
        media_ids.add(item_id)
        
        if item_id in scored_results:
            scored_results[item_id]["score"] += 0.1  # Metadata match small bonus
        else:
            scored_results[item_id] = {
                "score": 0.1,
                "metadata_match": True,
                "media_item": item
            }
    
    # 4. Combine and rank
    combined = []
    for media_id in media_ids:
        score_data = scored_results[media_id]
        
        # Get media item if not already loaded
        media_item = score_data.get("media_item")
        if not media_item:
            media_item = db.query(MediaItem).filter(MediaItem.id == media_id).first()
        
        if media_item:
            combined.append({
                "media_id": media_id,
                "score": round(score_data["score"], 4),
                "media_item": media_item,
                "matches": {
                    "semantic": "semantic_score" in score_data,
                    "tags": score_data.get("tag_match", False),
                    "metadata": score_data.get("metadata_match", False)
                }
            })
    
    # Sort by score descending
    combined.sort(key=lambda x: x["score"], reverse=True)
    
    results["combined"] = combined[skip:skip + limit]
    results["total"] = len(combined)
    
    return results


def get_search_suggestions(db: Session, partial: str, limit: int = 10) -> List[str]:
    """
    Get autocomplete suggestions for search.
    
    Returns matching tags, classifications, and filenames.
    """
    suggestions = set()
    
    # Tag suggestions
    tag_query = db.query(MediaTag.tag_value).filter(
        MediaTag.tag_value.ilike(f"%{partial}%")
    ).distinct().limit(limit)
    
    for row in tag_query:
        suggestions.add(row[0])
    
    # Classification suggestions
    class_query = db.query(MediaItem.classification).filter(
        MediaItem.classification.ilike(f"%{partial}%"),
        MediaItem.processing_status == "ready"
    ).distinct().limit(limit)
    
    for row in class_query:
        if row[0]:
            suggestions.add(row[0])
    
    return list(suggestions)[:limit]
