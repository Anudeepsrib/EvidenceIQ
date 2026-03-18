"""
EvidenceIQ Processing - CLIP Embeddings
Local image embeddings for semantic search via ChromaDB.
"""
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer

from app.config import settings

# Lazy-loaded CLIP model
_clip_model = None


def get_clip_model():
    """Lazy-load CLIP model."""
    global _clip_model
    if _clip_model is None:
        _clip_model = SentenceTransformer(settings.embedding_model)
    return _clip_model


def get_chroma_client():
    """Get ChromaDB client."""
    import chromadb
    return chromadb.PersistentClient(path=str(settings.resolved_chroma_path))


def get_or_create_collection():
    """Get or create the media embeddings collection."""
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name="media_embeddings",
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def compute_image_embedding(image_path: str) -> Optional[List[float]]:
    """
    Compute CLIP embedding for an image.
    
    Args:
        image_path: Path to image file
    
    Returns:
        Embedding vector as list of floats, or None if failed
    """
    try:
        model = get_clip_model()
        
        # Load and preprocess image
        image = Image.open(image_path)
        
        # Compute embedding
        embedding = model.encode(image)
        
        return embedding.tolist()
        
    except Exception as e:
        print(f"Error computing embedding for {image_path}: {e}")
        return None


def compute_text_embedding(text: str) -> Optional[List[float]]:
    """
    Compute CLIP embedding for text query.
    
    Args:
        text: Text query string
    
    Returns:
        Embedding vector as list of floats, or None if failed
    """
    try:
        model = get_clip_model()
        embedding = model.encode(text)
        return embedding.tolist()
        
    except Exception as e:
        print(f"Error computing text embedding: {e}")
        return None


def store_embedding(
    media_id: str,
    image_path: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Store image embedding in ChromaDB.
    
    Args:
        media_id: Media item ID
        image_path: Path to image file
        metadata: Dict with media metadata (classification, tags, etc.)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Compute embedding
        embedding = compute_image_embedding(image_path)
        
        if embedding is None:
            return False
        
        # Get collection
        collection = get_or_create_collection()
        
        # Prepare metadata for storage (ChromaDB requires strings)
        chroma_metadata = {
            "media_id": str(media_id),
            "classification": str(metadata.get("classification", "unknown")),
            "description": str(metadata.get("description", ""))[:500],  # Limit length
            "uploaded_by": str(metadata.get("uploaded_by", "")),
            "upload_date": str(metadata.get("upload_date", "")),
        }
        
        # Add tags as comma-separated string
        tags = metadata.get("tags", {})
        if isinstance(tags, dict):
            scene_tags = tags.get("scene_tags", [])
            if isinstance(scene_tags, list):
                chroma_metadata["tags"] = ",".join(scene_tags)
            else:
                chroma_metadata["tags"] = str(scene_tags)
        
        # Store in ChromaDB
        collection.upsert(
            ids=[media_id],
            embeddings=[embedding],
            metadatas=[chroma_metadata]
        )
        
        return True
        
    except Exception as e:
        print(f"Error storing embedding: {e}")
        return False


def semantic_search(
    query_text: str,
    top_k: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Perform semantic search using text query.
    
    Args:
        query_text: Natural language query
        top_k: Number of results to return
        filters: Optional metadata filters
    
    Returns:
        List of search results with media_id, score, and metadata
    """
    try:
        # Compute text embedding
        query_embedding = compute_text_embedding(query_text)
        
        if query_embedding is None:
            return []
        
        # Get collection
        collection = get_or_create_collection()
        
        # Build where clause if filters provided
        where_clause = None
        if filters:
            where_clause = build_where_clause(filters)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, media_id in enumerate(results["ids"][0]):
                score = results["distances"][0][i] if results["distances"] else 0
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                
                # Convert cosine distance to similarity score (0-1)
                similarity = 1 - score
                
                formatted_results.append({
                    "media_id": media_id,
                    "score": round(similarity, 4),
                    "metadata": metadata
                })
        
        return formatted_results
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return []


def build_where_clause(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Build ChromaDB where clause from filters."""
    where = {}
    
    if "classification" in filters:
        where["classification"] = filters["classification"]
    
    if "uploaded_by" in filters:
        where["uploaded_by"] = filters["uploaded_by"]
    
    return where if where else None


def delete_embedding(media_id: str) -> bool:
    """Delete embedding from ChromaDB."""
    try:
        collection = get_or_create_collection()
        collection.delete(ids=[media_id])
        return True
    except Exception as e:
        print(f"Error deleting embedding: {e}")
        return False


def get_embedding_stats() -> Dict[str, Any]:
    """Get statistics about stored embeddings."""
    try:
        collection = get_or_create_collection()
        count = collection.count()
        
        return {
            "total_embeddings": count,
            "collection_name": "media_embeddings"
        }
        
    except Exception as e:
        print(f"Error getting embedding stats: {e}")
        return {"total_embeddings": 0, "error": str(e)}
