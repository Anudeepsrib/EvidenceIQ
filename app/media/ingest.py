"""
EvidenceIQ Media Ingest Pipeline
MIME validation, filename sanitization, UUID path generation, EXIF extraction.
"""
import os
import re
import uuid
import hashlib
from urllib.parse import unquote
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from PIL import Image
import piexif

from app.config import settings

try:
    import magic
except Exception:
    magic = None

try:
    import filetype
except Exception:
    filetype = None

try:
    from presidio_analyzer import AnalyzerEngine
except Exception:
    AnalyzerEngine = None

# Accepted MIME types
ACCEPTED_IMAGE_TYPES = {
    'image/jpeg', 'image/png', 'image/tiff', 'image/webp'
}

ACCEPTED_VIDEO_TYPES = {
    'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'
}

ACCEPTED_DOCUMENT_TYPES = {
    'application/pdf'
}

ACCEPTED_TYPES = ACCEPTED_IMAGE_TYPES | ACCEPTED_VIDEO_TYPES | ACCEPTED_DOCUMENT_TYPES

# File extensions by MIME type
MIME_TO_EXT = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/tiff': '.tiff',
    'image/webp': '.webp',
    'video/mp4': '.mp4',
    'video/quicktime': '.mov',
    'video/x-msvideo': '.avi',
    'video/webm': '.webm',
    'application/pdf': '.pdf'
}

MIME_TO_ALLOWED_EXTENSIONS = {
    'image/jpeg': {'.jpg', '.jpeg'},
    'image/png': {'.png'},
    'image/tiff': {'.tif', '.tiff'},
    'image/webp': {'.webp'},
    'video/mp4': {'.mp4'},
    'video/quicktime': {'.mov', '.qt'},
    'video/x-msvideo': {'.avi'},
    'video/webm': {'.webm'},
    'application/pdf': {'.pdf'},
}

SENSITIVE_EXIF_FIELDS = {
    'GPSInfo': 'gps_coordinates',
    'GPSLatitude': 'gps_coordinates',
    'GPSLatitudeRef': 'gps_coordinates',
    'GPSLongitude': 'gps_coordinates',
    'GPSLongitudeRef': 'gps_coordinates',
    'GPSAltitude': 'gps_coordinates',
    'GPSAltitudeRef': 'gps_coordinates',
    'GPSDateStamp': 'gps_coordinates',
    'BodySerialNumber': 'camera_serial',
    'SerialNumber': 'camera_serial',
    'CameraOwnerName': 'owner_name',
    'OwnerName': 'owner_name',
    'Artist': 'owner_name',
    'Copyright': 'copyright',
    'ImageDescription': 'description',
    'UserComment': 'user_comment',
    'Software': 'software_version',
}

PII_PATTERNS = {
    "email": re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "medical_id": re.compile(r"(?i)\b(?:MRN|medical\s*record|patient\s*id|medical\s*id)\s*[:#-]?\s*[A-Z0-9-]{4,}\b"),
}

_pii_analyzer = None


class IngestError(Exception):
    """Custom exception for ingest pipeline errors."""
    def __init__(self, message: str, code: str = "ingest_error"):
        self.message = message
        self.code = code
        super().__init__(self.message)


def validate_mime_type(file_content: bytes, declared_type: Optional[str] = None) -> str:
    """
    Validate file MIME type using python-magic (libmagic).
    
    Args:
        file_content: Raw file bytes
        declared_type: Optional declared MIME type from client
    
    Returns:
        Detected MIME type
    
    Raises:
        IngestError: If MIME type is not accepted
    """
    detected = detect_mime_type(file_content)
    
    if detected not in ACCEPTED_TYPES:
        raise IngestError(
            f"Unsupported file type: {detected}. "
            f"Accepted: JPEG, PNG, TIFF, WEBP, MP4, MOV, AVI, PDF",
            code="unsupported_type"
        )
    
    return detected


def detect_mime_type(file_content: bytes) -> str:
    """Detect MIME type with libmagic when available, then pure-Python fallbacks."""
    if magic is not None:
        try:
            detected = magic.from_buffer(file_content, mime=True)
            if detected:
                return detected
        except Exception:
            pass

    if filetype is not None:
        guessed = filetype.guess(file_content)
        if guessed and guessed.mime:
            return guessed.mime

    # Minimal signature fallback for tests and Windows development without libmagic.
    if file_content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if file_content.startswith((b"II*\x00", b"MM\x00*")):
        return "image/tiff"
    if file_content.startswith(b"%PDF"):
        return "application/pdf"
    if len(file_content) > 12 and file_content[8:12] == b"WEBP":
        return "image/webp"
    if len(file_content) > 12 and file_content[4:8] == b"ftyp":
        brand = file_content[8:12]
        if brand in {b"qt  "}:
            return "video/quicktime"
        return "video/mp4"
    if file_content.startswith(b"RIFF") and len(file_content) > 12 and file_content[8:12] == b"AVI ":
        return "video/x-msvideo"
    if file_content.startswith(b"\x1aE\xdf\xa3"):
        return "video/webm"

    return "application/octet-stream"


def validate_file_extension(filename: str, mime_type: str) -> str:
    """Ensure the client filename extension is compatible with detected content."""
    suffix = Path(filename or "").suffix.lower()
    allowed = MIME_TO_ALLOWED_EXTENSIONS.get(mime_type, set())
    if not suffix or suffix not in allowed:
        raise IngestError(
            f"File extension '{suffix or '[none]'}' does not match detected type {mime_type}",
            code="invalid_extension",
        )
    return suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection.
    
    - Strips path traversal characters
    - Removes control characters
    - Enforces alphanumeric + dash + dot only
    - Preserves original extension
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename safe for storage
    """
    filename = unquote(filename or "")

    # Extract original extension
    original_path = Path(filename)
    original_ext = original_path.suffix.lower()
    
    # Get basename without path
    basename = os.path.basename(filename.replace("\\", "/"))
    
    # Remove control characters
    basename = ''.join(char for char in basename if ord(char) >= 32)
    
    # Replace dangerous characters with underscore
    # Allow: alphanumeric, dash, underscore, dot
    sanitized = re.sub(r'[^a-zA-Z0-9\-_\.]', '_', basename)
    
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Ensure it doesn't start with dot (hidden file)
    sanitized = sanitized.lstrip('.')
    
    # Limit length
    max_length = 200
    if len(sanitized) > max_length:
        name_part = sanitized[:max_length]
        # Ensure we keep the extension
        if original_ext and not name_part.endswith(original_ext):
            sanitized = name_part[:max_length - len(original_ext)] + original_ext
        else:
            sanitized = name_part
    
    # If empty after sanitization, generate a default name
    if not sanitized or sanitized == original_ext:
        sanitized = f"upload_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{original_ext}"
    
    return sanitized


def generate_storage_path(mime_type: str) -> Tuple[str, str, Path]:
    """
    Generate UUID-based internal storage path.
    
    Creates a hierarchical structure: uploads/YY/MM/DD/uuid.ext
    This prevents single-directory overload and improves filesystem performance.
    
    Args:
        mime_type: MIME type for determining extension
    
    Returns:
        Tuple of (uuid, extension, full_storage_path)
    """
    file_uuid = str(uuid.uuid4())
    ext = MIME_TO_EXT.get(mime_type, '.bin')
    
    # Create date-based hierarchy
    now = datetime.utcnow()
    date_path = f"{now.year % 100:02d}/{now.month:02d}/{now.day:02d}"
    
    # Full relative path
    relative_path = f"uploads/{date_path}/{file_uuid}{ext}"
    
    # Full absolute path
    full_path = settings.resolved_storage_path / relative_path
    
    return file_uuid, ext, full_path


def compute_sha256(file_content: bytes) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def verify_file_hash(file_path: Path, expected_hash: str) -> bool:
    """Verify file integrity against stored hash."""
    with open(file_path, 'rb') as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    return actual_hash == expected_hash


def extract_exif_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extract EXIF metadata from image file.
    
    Args:
        file_path: Path to image file
    
    Returns:
        Dictionary of EXIF data or empty dict if none/no EXIF
    """
    try:
        img = Image.open(file_path)
        exif_dict = piexif.load(img.info.get('exif', b''))
        
        metadata = {}
        
        # Extract useful EXIF data
        for ifd in exif_dict:
            if ifd == "thumbnail":
                continue
            for tag, value in exif_dict[ifd].items():
                tag_name = piexif.TAGS.get(ifd, {}).get(tag, {}).get("name", tag)
                try:
                    # Decode bytes to string
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='ignore').strip('\x00')
                    metadata[tag_name] = value
                except Exception:
                    metadata[tag_name] = str(value)
        
        return metadata
        
    except Exception:
        return {}


def _get_pii_analyzer():
    """Load Presidio lazily so missing heavy models do not break app startup."""
    global _pii_analyzer
    if not settings.enable_pii_scrubbing or AnalyzerEngine is None:
        return None
    if _pii_analyzer is None:
        try:
            _pii_analyzer = AnalyzerEngine()
        except Exception:
            _pii_analyzer = None
    return _pii_analyzer


def detect_pii_in_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect PII in EXIF metadata using presidio-analyzer.
    
    Returns:
        Dictionary with pii_detected flag and detected types
    """
    if not settings.enable_pii_scrubbing:
        return {"pii_detected": False, "fields": []}
    
    pii_fields = []
    
    for field, pii_type in SENSITIVE_EXIF_FIELDS.items():
        if field in metadata and metadata[field]:
            pii_fields.append({
                "field": field,
                "type": pii_type,
                "action": "flagged"
            })

    analyzer = _get_pii_analyzer()

    for field, value in metadata.items():
        if not value:
            continue

        text = str(value)
        detected_types = set()

        for pii_type, pattern in PII_PATTERNS.items():
            if pattern.search(text):
                detected_types.add(pii_type)

        if analyzer is not None:
            try:
                results = analyzer.analyze(text=text, language="en")
                detected_types.update(result.entity_type.lower() for result in results)
            except Exception:
                pass

        for pii_type in sorted(detected_types):
            pii_fields.append({
                "field": field,
                "type": pii_type,
                "action": "redacted"
            })
    
    return {
        "pii_detected": len(pii_fields) > 0,
        "fields": pii_fields
    }


def redact_pii_text(value: Any) -> Any:
    """Redact common PII patterns from a metadata value."""
    if not isinstance(value, str):
        return value

    redacted = value
    for pii_type, pattern in PII_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted)
    return redacted


def scrub_metadata_for_display(metadata: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Remove sensitive EXIF fields and redact PII before API/report exposure."""
    flags = detect_pii_in_metadata(metadata)
    safe_metadata: Dict[str, Any] = {}

    for field, value in metadata.items():
        if field in SENSITIVE_EXIF_FIELDS:
            continue
        safe_metadata[field] = redact_pii_text(value)

    return safe_metadata, flags


def get_image_dimensions(file_path: Path) -> Tuple[Optional[int], Optional[int]]:
    """Get image/video dimensions."""
    try:
        if file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.webm']:
            # Video dimensions via OpenCV
            import cv2
            cap = cv2.VideoCapture(str(file_path))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return width, height
        else:
            # Image dimensions via PIL
            with Image.open(file_path) as img:
                return img.width, img.height
    except Exception:
        return None, None


def get_video_duration(file_path: Path) -> Optional[float]:
    """Get video duration in seconds."""
    try:
        import cv2
        cap = cv2.VideoCapture(str(file_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        
        if fps > 0 and frame_count > 0:
            return frame_count / fps
        return None
    except Exception:
        return None


def process_upload(
    filename: str,
    file_content: bytes,
    uploader_id: str,
    precomputed_sha256: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main ingest pipeline entry point.
    
    Args:
        filename: Original filename
        file_content: Raw file bytes
        uploader_id: User ID who uploaded the file
    
    Returns:
        Dictionary with all processed data ready for database insertion
    
    Raises:
        IngestError: If any validation fails
    """
    # Step 1: Validate file size
    if len(file_content) > settings.max_file_size_bytes:
        raise IngestError(
            f"File too large: {len(file_content)} bytes. "
            f"Maximum: {settings.max_file_size_mb}MB",
            code="file_too_large"
        )
    
    # Step 2: Validate MIME type
    mime_type = validate_mime_type(file_content)
    
    # Step 3: Sanitize filename
    validate_file_extension(filename, mime_type)
    safe_filename = sanitize_filename(filename)
    
    # Step 4: Generate storage path
    file_uuid, ext, storage_path = generate_storage_path(mime_type)
    
    # Step 5: Ensure directory exists
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Step 6: Compute hash
    sha256_hash = precomputed_sha256 or compute_sha256(file_content)
    
    # Step 7: Write file to storage
    try:
        with open(storage_path, 'wb') as f:
            f.write(file_content)

        # Step 8: Extract metadata and dimensions
        exif_metadata = {}
        pii_flags = {}
        width, height = None, None
        duration = None

        if mime_type in ACCEPTED_IMAGE_TYPES:
            raw_exif_metadata = extract_exif_metadata(storage_path)
            exif_metadata, pii_flags = scrub_metadata_for_display(raw_exif_metadata)
            width, height = get_image_dimensions(storage_path)

        elif mime_type in ACCEPTED_VIDEO_TYPES:
            width, height = get_image_dimensions(storage_path)
            duration = get_video_duration(storage_path)
    except IngestError:
        if storage_path.exists():
            storage_path.unlink()
        raise
    except Exception as e:
        if storage_path.exists():
            storage_path.unlink()
        raise IngestError(f"Failed to process file: {str(e)}", code="processing_error")
    
    # Step 9: Return processed data
    return {
        "uuid": file_uuid,
        "original_filename": safe_filename,
        "internal_path": storage_path.relative_to(settings.resolved_storage_path).as_posix(),
        "mime_type": mime_type,
        "file_size_bytes": len(file_content),
        "sha256_hash": sha256_hash,
        "width_px": width,
        "height_px": height,
        "duration_seconds": duration,
        "uploaded_by": uploader_id,
        "exif_metadata": exif_metadata,
        "pii_flags": pii_flags,
        "processing_status": "pending"
    }
