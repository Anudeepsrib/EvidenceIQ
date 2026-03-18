"""
EvidenceIQ Processing - PDF Image Extraction
PyMuPDF-based embedded image extraction from PDFs.
"""
import uuid
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

import fitz  # PyMuPDF

from app.config import settings


def extract_images_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract all embedded images from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        List of extracted image data dicts
    """
    extracted_images = []
    
    try:
        # Open PDF
        pdf_document = fitz.open(pdf_path)
        
        # Storage setup
        storage_root = settings.resolved_storage_path
        date_path = datetime.utcnow().strftime("%y/%m/%d")
        pdf_dir = storage_root / "uploads" / date_path
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        # Track unique images (avoid duplicates across pages)
        seen_hashes = set()
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Get images on this page
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                
                try:
                    # Extract image
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Skip if we've seen this exact image before
                    import hashlib
                    img_hash = hashlib.md5(image_bytes).hexdigest()
                    if img_hash in seen_hashes:
                        continue
                    seen_hashes.add(img_hash)
                    
                    # Generate UUID and path
                    img_uuid = str(uuid.uuid4())
                    img_filename = f"{img_uuid}.{image_ext}"
                    img_path = pdf_dir / img_filename
                    
                    # Save image
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Get image dimensions if possible
                    width = base_image.get("width")
                    height = base_image.get("height")
                    
                    extracted_images.append({
                        "uuid": img_uuid,
                        "page_number": page_num + 1,
                        "image_index": img_index,
                        "extracted_path": str(img_path.relative_to(storage_root)),
                        "mime_type": f"image/{image_ext}",
                        "file_size_bytes": len(image_bytes),
                        "width_px": width,
                        "height_px": height,
                        "sha256_hash": hashlib.sha256(image_bytes).hexdigest()
                    })
                    
                except Exception as e:
                    print(f"Error extracting image {img_index} from page {page_num}: {e}")
                    continue
        
        pdf_document.close()
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []
    
    return extracted_images


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Get PDF metadata without extracting images.
    
    Returns:
        Dict with PDF properties
    """
    try:
        pdf_document = fitz.open(pdf_path)
        
        info = {
            "page_count": len(pdf_document),
            "title": pdf_document.metadata.get("title", ""),
            "author": pdf_document.metadata.get("author", ""),
            "subject": pdf_document.metadata.get("subject", ""),
            "creator": pdf_document.metadata.get("creator", ""),
            "producer": pdf_document.metadata.get("producer", ""),
            "creation_date": pdf_document.metadata.get("creationDate", ""),
            "modification_date": pdf_document.metadata.get("modDate", ""),
        }
        
        pdf_document.close()
        
        return info
        
    except Exception:
        return {}


def is_pdf(file_path: str) -> bool:
    """Check if a file is a valid PDF."""
    try:
        pdf_document = fitz.open(file_path)
        is_valid = pdf_document.is_pdf
        pdf_document.close()
        return is_valid
    except Exception:
        return False


def count_pdf_images(pdf_path: str) -> int:
    """Count total embedded images in PDF (for estimation)."""
    try:
        pdf_document = fitz.open(pdf_path)
        total_images = 0
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            image_list = page.get_images()
            total_images += len(image_list)
        
        pdf_document.close()
        
        return total_images
        
    except Exception:
        return 0
