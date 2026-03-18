"""
EvidenceIQ Processing - Video Frame Extraction
OpenCV-based keyframe extraction for video processing.
"""
import cv2
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.config import settings


def extract_video_frames(
    video_path: str,
    interval_seconds: int = None
) -> List[Dict[str, Any]]:
    """
    Extract keyframes from video at specified interval.
    
    Args:
        video_path: Path to video file
        interval_seconds: Seconds between frames (default: from settings)
    
    Returns:
        List of frame data dicts with:
        - frame_number: Frame index
        - timestamp_seconds: Timestamp in video
        - extracted_path: Path to saved frame image
        - uuid: UUID for the frame
    """
    if interval_seconds is None:
        interval_seconds = settings.video_frame_interval_seconds
    
    frames = []
    
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Calculate frame interval
        frame_interval = int(fps * interval_seconds)
        if frame_interval < 1:
            frame_interval = 1
        
        # Extract frames
        frame_number = 0
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Process frame at interval
            if frame_number % frame_interval == 0:
                timestamp = frame_number / fps if fps > 0 else 0
                
                # Generate UUID for frame
                frame_uuid = str(uuid.uuid4())
                
                # Save frame
                storage_root = settings.resolved_storage_path
                date_path = datetime.utcnow().strftime("%y/%m/%d")
                frame_dir = storage_root / "uploads" / date_path
                frame_dir.mkdir(parents=True, exist_ok=True)
                
                frame_filename = f"{frame_uuid}.jpg"
                frame_path = frame_dir / frame_filename
                
                # Convert BGR to RGB and save
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.imwrite(str(frame_path), frame_rgb)
                
                # Compute file size
                file_size = frame_path.stat().st_size
                
                # Get dimensions
                height, width = frame.shape[:2]
                
                frames.append({
                    "uuid": frame_uuid,
                    "frame_number": frame_number,
                    "timestamp_seconds": round(timestamp, 2),
                    "extracted_path": str(frame_path.relative_to(storage_root)),
                    "mime_type": "image/jpeg",
                    "file_size_bytes": file_size,
                    "width_px": width,
                    "height_px": height,
                    "sha256_hash": None  # Will be computed during ingest
                })
            
            frame_number += 1
        
        cap.release()
        
    except Exception as e:
        print(f"Error extracting frames: {e}")
        return []
    
    return frames


def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get video metadata without extracting frames.
    
    Returns:
        Dict with video properties
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        duration = total_frames / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "duration_seconds": round(duration, 2),
            "total_frames": total_frames,
            "fps": round(fps, 2),
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}"
        }
        
    except Exception:
        return {}


def extract_single_frame(video_path: str, timestamp_seconds: float) -> Optional[str]:
    """
    Extract a single frame at a specific timestamp.
    
    Args:
        video_path: Path to video file
        timestamp_seconds: Timestamp to extract frame at
    
    Returns:
        Path to extracted frame image, or None if failed
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        # Get FPS and calculate frame number
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp_seconds * fps)
        
        # Set position and read frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if not ret:
            cap.release()
            return None
        
        # Generate path
        frame_uuid = str(uuid.uuid4())
        storage_root = settings.resolved_storage_path
        date_path = datetime.utcnow().strftime("%y/%m/%d")
        frame_dir = storage_root / "uploads" / date_path
        frame_dir.mkdir(parents=True, exist_ok=True)
        
        frame_path = frame_dir / f"{frame_uuid}.jpg"
        
        # Save frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(str(frame_path), frame_rgb)
        
        cap.release()
        
        return str(frame_path.relative_to(storage_root))
        
    except Exception:
        return None
