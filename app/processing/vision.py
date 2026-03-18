"""
EvidenceIQ Processing - Vision Module
LLaVA, BakLLaVA, Moondream via Ollama for classification, description, and tagging.
"""
import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path

import ollama
from PIL import Image

from app.config import settings

# Vision model prompt templates
CLASSIFICATION_PROMPT = """Analyze this image and classify it into exactly one of these categories:
- document: Text-heavy document, form, letter, contract
- photograph: Regular photo of people, places, objects
- screenshot: Digital screenshot, UI capture, software interface
- diagram: Technical diagram, chart, graph, blueprint
- surveillance_still: Security camera footage, surveillance image
- medical_image: Medical scan, X-ray, MRI, pathology image
- chart: Data visualization, bar chart, pie chart, line graph
- mixed: Multiple content types in one image
- unknown: Cannot determine category

Respond with ONLY the category name, nothing else."""

DESCRIPTION_PROMPT = """Describe this image in 2-3 factual sentences.
Focus on: what is depicted, main subjects, setting, visible objects.
Do NOT include opinions, interpretations, or assumptions.
Be objective and descriptive."""

TAGGING_PROMPT = """Analyze this image and return a JSON object with these fields:
{
  "people_present": boolean,
  "estimated_people_count": integer or null,
  "faces_visible": boolean,
  "text_visible": boolean,
  "location_type": "indoor" | "outdoor" | "unknown",
  "time_of_day": "day" | "night" | "unclear" | "unknown",
  "objects": ["list", "of", "main", "objects"],
  "scene_tags": ["list", "of", "descriptive", "tags"],
  "sensitive_content_flags": ["violence" | "nudity" | "medical" | "legal_document" | "financial_document" | "none"]
}

Return ONLY valid JSON, no markdown fences, no additional text."""


class VisionError(Exception):
    """Custom exception for vision processing errors."""
    pass


def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for Ollama vision models."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def resize_for_vision(image_path: str, max_size: int = 512) -> str:
    """
    Resize image for vision model input.
    Returns path to temporary resized image.
    """
    from PIL import Image
    import tempfile
    
    img = Image.open(image_path)
    
    # Resize maintaining aspect ratio
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Convert to RGB for consistency
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(temp_file.name, "JPEG", quality=85)
    temp_file.close()
    
    return temp_file.name


def classify_image(image_path: str, model: str = None) -> Dict[str, Any]:
    """
    Classify image using vision model.
    
    Returns:
        Dict with classification result and confidence
    """
    if model is None:
        model = settings.vision_model_default
    
    try:
        # Resize image for faster processing
        resized_path = resize_for_vision(image_path)
        
        # Get Ollama client
        client = ollama.Client(host=settings.ollama_base_url)
        
        # Call vision model
        response = client.generate(
            model=model,
            prompt=CLASSIFICATION_PROMPT,
            images=[resized_path]
        )
        
        # Clean up temp file
        import os
        os.unlink(resized_path)
        
        # Parse response
        classification = response.response.strip().lower()
        
        # Validate classification
        valid_classifications = [
            "document", "photograph", "screenshot", "diagram",
            "surveillance_still", "medical_image", "chart", "mixed", "unknown"
        ]
        
        if classification not in valid_classifications:
            classification = "unknown"
        
        return {
            "classification": classification,
            "raw_response": response.response,
            "model_used": model,
            "success": True
        }
        
    except Exception as e:
        return {
            "classification": "unknown",
            "error": str(e),
            "model_used": model,
            "success": False
        }


def describe_image(image_path: str, model: str = None) -> Dict[str, Any]:
    """
    Generate factual description of image using vision model.
    
    Returns:
        Dict with description and model info
    """
    if model is None:
        model = settings.vision_model_default
    
    try:
        # Resize image
        resized_path = resize_for_vision(image_path)
        
        # Get Ollama client
        client = ollama.Client(host=settings.ollama_base_url)
        
        # Call vision model
        response = client.generate(
            model=model,
            prompt=DESCRIPTION_PROMPT,
            images=[resized_path]
        )
        
        # Clean up temp file
        import os
        os.unlink(resized_path)
        
        return {
            "description": response.response.strip(),
            "model_used": model,
            "success": True
        }
        
    except Exception as e:
        return {
            "description": "",
            "error": str(e),
            "model_used": model,
            "success": False
        }


def tag_image(image_path: str, model: str = None) -> Dict[str, Any]:
    """
    Extract structured tags from image using vision model.
    
    Returns:
        Dict with structured tags
    """
    if model is None:
        model = settings.vision_model_default
    
    try:
        # Resize image
        resized_path = resize_for_vision(image_path)
        
        # Get Ollama client
        client = ollama.Client(host=settings.ollama_base_url)
        
        # Call vision model
        response = client.generate(
            model=model,
            prompt=TAGGING_PROMPT,
            images=[resized_path]
        )
        
        # Clean up temp file
        import os
        os.unlink(resized_path)
        
        # Parse JSON response
        raw_response = response.response.strip()
        
        # Remove markdown fences if present
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[1]
        if raw_response.endswith("```"):
            raw_response = raw_response.rsplit("```", 1)[0]
        raw_response = raw_response.strip()
        
        try:
            tags = json.loads(raw_response)
        except json.JSONDecodeError:
            # Fallback: try to extract any JSON-like structure
            tags = {
                "people_present": False,
                "estimated_people_count": None,
                "faces_visible": False,
                "text_visible": False,
                "location_type": "unknown",
                "time_of_day": "unknown",
                "objects": [],
                "scene_tags": [],
                "sensitive_content_flags": ["none"],
                "parse_error": True,
                "raw_response": raw_response[:200]
            }
        
        return {
            "tags": tags,
            "model_used": model,
            "success": True
        }
        
    except Exception as e:
        return {
            "tags": {
                "people_present": False,
                "estimated_people_count": None,
                "faces_visible": False,
                "text_visible": False,
                "location_type": "unknown",
                "time_of_day": "unknown",
                "objects": [],
                "scene_tags": [],
                "sensitive_content_flags": ["none"]
            },
            "error": str(e),
            "model_used": model,
            "success": False
        }


def process_image_full(image_path: str, model: str = None) -> Dict[str, Any]:
    """
    Run full vision pipeline on image: classify, describe, tag.
    
    Each step runs sequentially. If one fails, others continue.
    
    Returns:
        Complete processing results
    """
    if model is None:
        model = settings.vision_model_default
    
    results = {
        "model_used": model,
        "steps_completed": [],
        "steps_failed": [],
        "classification": None,
        "description": None,
        "tags": None
    }
    
    # Step 1: Classification
    classification_result = classify_image(image_path, model)
    if classification_result["success"]:
        results["classification"] = classification_result["classification"]
        results["steps_completed"].append("classification")
    else:
        results["steps_failed"].append("classification")
        results["classification"] = "unknown"
    
    # Step 2: Description
    description_result = describe_image(image_path, model)
    if description_result["success"]:
        results["description"] = description_result["description"]
        results["steps_completed"].append("description")
    else:
        results["steps_failed"].append("description")
        results["description"] = ""
    
    # Step 3: Tagging
    tagging_result = tag_image(image_path, model)
    if tagging_result["success"]:
        results["tags"] = tagging_result["tags"]
        results["steps_completed"].append("tagging")
    else:
        results["steps_failed"].append("tagging")
        results["tags"] = {
            "people_present": False,
            "estimated_people_count": None,
            "faces_visible": False,
            "text_visible": False,
            "location_type": "unknown",
            "time_of_day": "unknown",
            "objects": [],
            "scene_tags": [],
            "sensitive_content_flags": ["none"]
        }
    
    results["success"] = len(results["steps_completed"]) > 0
    
    return results


def check_model_availability(model: str) -> bool:
    """Check if a vision model is available in Ollama."""
    try:
        client = ollama.Client(host=settings.ollama_base_url)
        client.show(model)
        return True
    except Exception:
        return False


def list_available_models() -> list:
    """List all available Ollama models."""
    try:
        client = ollama.Client(host=settings.ollama_base_url)
        models = client.list()
        return [m.model for m in models.models]
    except Exception:
        return []
