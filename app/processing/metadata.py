"""
EvidenceIQ Processing - Metadata Module
EXIF extraction and PII scrubbing from image metadata.
"""
from typing import List, Dict, Any
from pathlib import Path

from PIL import Image
import piexif


def scrub_exif_metadata(
    input_path: str,
    output_path: str,
    scrub_gps: bool = True,
    scrub_camera_serial: bool = True,
    scrub_owner: bool = True,
    scrub_software: bool = True,
    scrub_dates: bool = False
) -> List[str]:
    """
    Scrub PII from image EXIF metadata and save to new file.
    
    Original file is NEVER modified. A new redacted copy is created.
    
    Args:
        input_path: Path to original image
        output_path: Path to save redacted image
        scrub_gps: Remove GPS coordinates
        scrub_camera_serial: Remove camera serial numbers
        scrub_owner: Remove owner/artist fields
        scrub_software: Remove software version (fingerprinting)
        scrub_dates: Remove date fields
    
    Returns:
        List of field names that were scrubbed
    """
    # Open image
    img = Image.open(input_path)
    
    # Get existing EXIF data
    try:
        exif_dict = piexif.load(img.info.get('exif', b''))
    except Exception:
        exif_dict = {"0th": {}, "1st": {}, "Exif": {}, "GPS": {}, "Interop": {}}
    
    scrubbed_fields = []
    
    # Define EXIF tags to scrub
    tags_to_scrub = {}
    
    if scrub_gps:
        # GPSInfo is in GPS IFD
        tags_to_scrub["GPS"] = [
            piexif.GPSIFD.GPSVersionID,
            piexif.GPSIFD.GPSLatitudeRef,
            piexif.GPSIFD.GPSLatitude,
            piexif.GPSIFD.GPSLongitudeRef,
            piexif.GPSIFD.GPSLongitude,
            piexif.GPSIFD.GPSAltitudeRef,
            piexif.GPSIFD.GPSAltitude,
            piexif.GPSIFD.GPSTimestamp,
            piexif.GPSIFD.GPSSatellites,
            piexif.GPSIFD.GPSStatus,
            piexif.GPSIFD.GPSMeasureMode,
            piexif.GPSIFD.GPSDOP,
            piexif.GPSIFD.GPSSpeedRef,
            piexif.GPSIFD.GPSSpeed,
            piexif.GPSIFD.GPSTrackRef,
            piexif.GPSIFD.GPSTrack,
            piexif.GPSIFD.GPSImgDirectionRef,
            piexif.GPSIFD.GPSImgDirection,
            piexif.GPSIFD.GPSMapDatum,
            piexif.GPSIFD.GPSDestLatitudeRef,
            piexif.GPSIFD.GPSDestLatitude,
            piexif.GPSIFD.GPSDestLongitudeRef,
            piexif.GPSIFD.GPSDestLongitude,
            piexif.GPSIFD.GPSDestBearingRef,
            piexif.GPSIFD.GPSDestBearing,
            piexif.GPSIFD.GPSDestDistanceRef,
            piexif.GPSIFD.GPSDestDistance,
            piexif.GPSIFD.GPSProcessingMethod,
            piexif.GPSIFD.GPSAreaInformation,
            piexif.GPSIFD.GPSDateStamp,
            piexif.GPSIFD.GPSDifferential,
        ]
    
    if scrub_camera_serial:
        tags_to_scrub["0th"] = [
            piexif.ImageIFD.BodySerialNumber,
            piexif.ImageIFD.CameraOwnerName,
        ]
    
    if scrub_owner:
        tags_to_scrub["0th"].extend([
            piexif.ImageIFD.Artist,
            piexif.ImageIFD.Copyright,
        ])
    
    if scrub_software:
        tags_to_scrub["0th"].append(piexif.ImageIFD.Software)
    
    if scrub_dates:
        tags_to_scrub["0th"].extend([
            piexif.ImageIFD.DateTime,
        ])
        tags_to_scrub["Exif"] = [
            piexif.ExifIFD.DateTimeOriginal,
            piexif.ExifIFD.DateTimeDigitized,
        ]
    
    # Remove specified tags
    for ifd_name, tags in tags_to_scrub.items():
        if ifd_name in exif_dict:
            for tag in tags:
                tag_name = piexif.TAGS.get(ifd_name, {}).get(tag, {}).get("name", str(tag))
                if tag in exif_dict[ifd_name]:
                    del exif_dict[ifd_name][tag]
                    scrubbed_fields.append(f"{ifd_name}.{tag_name}")
    
    # Remove empty IFDs
    for ifd_name in list(exif_dict.keys()):
        if ifd_name != "thumbnail" and not exif_dict[ifd_name]:
            del exif_dict[ifd_name]
    
    # Convert to bytes
    exif_bytes = piexif.dump(exif_dict)
    
    # Convert to RGB for JPEG if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Save with scrubbed EXIF
    img.save(output_path, "JPEG", exif=exif_bytes, quality=95)
    
    return scrubbed_fields


def extract_safe_exif(file_path: str) -> Dict[str, Any]:
    """
    Extract EXIF metadata that is safe to expose (no PII).
    
    Returns filtered metadata suitable for viewer role.
    """
    try:
        img = Image.open(file_path)
        exif_dict = piexif.load(img.info.get('exif', b''))
        
        # Safe fields to expose
        safe_fields = {
            "ImageWidth": piexif.ImageIFD.ImageWidth,
            "ImageLength": piexif.ImageIFD.ImageLength,
            "BitsPerSample": piexif.ImageIFD.BitsPerSample,
            "Compression": piexif.ImageIFD.Compression,
            "PhotometricInterpretation": piexif.ImageIFD.PhotometricInterpretation,
            "Orientation": piexif.ImageIFD.Orientation,
            "SamplesPerPixel": piexif.ImageIFD.SamplesPerPixel,
            "PlanarConfiguration": piexif.ImageIFD.PlanarConfiguration,
            "YCbCrSubSampling": piexif.ImageIFD.YCbCrSubSampling,
            "YCbCrPositioning": piexif.ImageIFD.YCbCrPositioning,
            "XResolution": piexif.ImageIFD.XResolution,
            "YResolution": piexif.ImageIFD.YResolution,
            "ResolutionUnit": piexif.ImageIFD.ResolutionUnit,
            "Make": piexif.ImageIFD.Make,
            "Model": piexif.ImageIFD.Model,
        }
        
        safe_metadata = {}
        
        for field_name, tag_id in safe_fields.items():
            if tag_id in exif_dict.get("0th", {}):
                value = exif_dict["0th"][tag_id]
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8', errors='ignore').strip('\x00')
                    except:
                        value = str(value)
                safe_metadata[field_name] = value
        
        return safe_metadata
        
    except Exception:
        return {}


def get_exif_summary(file_path: str) -> Dict[str, Any]:
    """
    Get a summary of EXIF data for evidence reports.
    
    Includes only factual technical metadata, no PII.
    """
    safe_exif = extract_safe_exif(file_path)
    
    summary = {
        "dimensions": {
            "width": safe_exif.get("ImageWidth"),
            "height": safe_exif.get("ImageLength")
        },
        "camera": {
            "make": safe_exif.get("Make"),
            "model": safe_exif.get("Model")
        },
        "technical": {
            "orientation": safe_exif.get("Orientation"),
            "resolution_unit": safe_exif.get("ResolutionUnit"),
            "x_resolution": safe_exif.get("XResolution"),
            "y_resolution": safe_exif.get("YResolution")
        }
    }
    
    return summary
