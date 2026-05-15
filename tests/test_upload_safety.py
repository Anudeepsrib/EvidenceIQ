from io import BytesIO
from types import SimpleNamespace

import pytest
from PIL import Image

from app.media import ingest
from app.media.service import get_file_path


def make_png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (1, 1), color=(255, 255, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.parametrize(
    "filename",
    [
        "../evil.jpg",
        "..\\evil.jpg",
        "%2e%2e%2fevil.jpg",
        "C:\\Windows\\system32\\evil.jpg",
        "/tmp/evil.jpg",
    ],
)
def test_sanitize_filename_neutralizes_traversal(filename):
    sanitized = ingest.sanitize_filename(filename)
    assert ".." not in sanitized
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert sanitized


def test_process_upload_rejects_extension_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.settings, "storage_root", str(tmp_path))
    png_bytes = make_png_bytes()

    with pytest.raises(ingest.IngestError) as exc:
        ingest.process_upload("image.exe", png_bytes, uploader_id="user-1")

    assert exc.value.code == "invalid_extension"
    assert not list(tmp_path.rglob("*"))


def test_process_upload_uses_generated_storage_name(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest.settings, "storage_root", str(tmp_path))
    png_bytes = make_png_bytes()

    media_data = ingest.process_upload("../case.png", png_bytes, uploader_id="user-1")

    assert media_data["internal_path"].startswith("uploads/")
    assert ".." not in media_data["internal_path"]
    assert media_data["original_filename"] == "case.png"
    assert (tmp_path / media_data["internal_path"]).exists()


@pytest.mark.parametrize(
    "internal_path",
    [
        "../outside.png",
        "/tmp/outside.png",
        "uploads/../../outside.png",
        "C:\\Windows\\system32\\drivers\\etc\\hosts",
    ],
)
def test_get_file_path_rejects_traversal(internal_path, tmp_path, monkeypatch):
    from app.media import service as media_service

    monkeypatch.setattr(media_service.settings, "storage_root", str(tmp_path))
    media = SimpleNamespace(internal_path=internal_path, redacted_path=None)

    assert get_file_path(media) is None
