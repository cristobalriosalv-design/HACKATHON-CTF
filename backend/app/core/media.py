import os
from pathlib import Path

UPLOAD_ROOT = Path("uploads").resolve()


def get_media_base_url() -> str | None:
    value = os.getenv("MEDIA_BASE_URL", "").strip()
    if not value:
        return None
    return value.rstrip("/")


def build_media_url_for_file(file_path: str) -> str | None:
    base_url = get_media_base_url()
    if not base_url:
        return None

    path = Path(file_path)
    try:
        relative_path = path.resolve().relative_to(UPLOAD_ROOT)
    except ValueError:
        # Fall back to filename when path is outside the uploads directory.
        relative_path = Path(path.name)

    relative_url = "/".join(relative_path.parts)
    if not relative_url:
        return base_url
    return f"{base_url}/{relative_url}"
