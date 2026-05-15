from io import BytesIO

from PIL import Image
import piexif

from app.media.ingest import scrub_metadata_for_display
from app.processing.metadata import extract_safe_exif, scrub_exif_metadata


def test_metadata_display_scrubs_gps_and_device_identifiers():
    metadata = {
        "GPSInfo": {"lat": "41.8781", "lon": "-87.6298"},
        "BodySerialNumber": "CAMERA-SERIAL-123",
        "OwnerName": "Case Owner",
        "Software": "CameraOS 1.2.3",
        "Make": "ExampleCam",
        "Model": "X100",
    }

    safe_metadata, flags = scrub_metadata_for_display(metadata)

    assert "GPSInfo" not in safe_metadata
    assert "BodySerialNumber" not in safe_metadata
    assert "OwnerName" not in safe_metadata
    assert "Software" not in safe_metadata
    assert safe_metadata["Make"] == "ExampleCam"
    assert flags["pii_detected"] is True


def test_metadata_display_redacts_email_phone_ssn_and_medical_id():
    metadata = {
        "Comment": (
            "Contact jane@example.com or 312-555-0199. "
            "SSN 123-45-6789. MRN: A1234567."
        )
    }

    safe_metadata, flags = scrub_metadata_for_display(metadata)
    comment = safe_metadata["Comment"]

    assert "jane@example.com" not in comment
    assert "312-555-0199" not in comment
    assert "123-45-6789" not in comment
    assert "A1234567" not in comment
    detected_types = {field["type"] for field in flags["fields"]}
    assert {"email", "phone", "ssn", "medical_id"}.issubset(detected_types)


def test_gps_exif_redaction_creates_copy_without_gps(tmp_path):
    original = tmp_path / "original.jpg"
    redacted = tmp_path / "redacted.jpg"

    image = Image.new("RGB", (10, 10), color=(255, 255, 255))
    exif_dict = {
        "0th": {piexif.ImageIFD.Make: b"ExampleCam"},
        "Exif": {},
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: b"N",
            piexif.GPSIFD.GPSLatitude: ((41, 1), (52, 1), (0, 1)),
            piexif.GPSIFD.GPSLongitudeRef: b"W",
            piexif.GPSIFD.GPSLongitude: ((87, 1), (37, 1), (0, 1)),
        },
        "1st": {},
        "thumbnail": None,
    }

    buffer = BytesIO()
    image.save(buffer, format="JPEG", exif=piexif.dump(exif_dict))
    original.write_bytes(buffer.getvalue())

    scrubbed_fields = scrub_exif_metadata(str(original), str(redacted), scrub_gps=True)
    safe_exif = extract_safe_exif(str(redacted))
    redacted_exif = piexif.load(str(redacted))

    assert original.read_bytes() != redacted.read_bytes()
    assert any(field.startswith("GPS.") for field in scrubbed_fields)
    assert redacted_exif.get("GPS", {}) == {}
    assert safe_exif["Make"] == "ExampleCam"
