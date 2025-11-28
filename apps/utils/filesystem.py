import os
import shutil
import mimetypes
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from datetime import datetime

ROOT_PATH = Path(settings.VUEFINDER_ROOT)


def get_absolute_path(relative_path: str) -> Path:
    path = (ROOT_PATH / relative_path.lstrip("/")).resolve()
    # Security: prevent directory traversal
    path.relative_to(ROOT_PATH)
    return path


def format_item(path: Path, name: str = None):
    stat = path.stat()
    is_dir = path.is_dir()
    mime, _ = mimetypes.guess_type(path)
    return {
        "name": name or path.name,
        "path": str(path.relative_to(ROOT_PATH).as_posix()).replace("\\", "/"),
        "type": "dir" if is_dir else "file",
        "mime_type": "directory" if is_dir else (mime or "application/octet-stream"),
        "size": stat.st_size if not is_dir else 0,
        "created": timezone.make_aware(datetime.fromtimestamp(stat.st_ctime)),
        "modified": timezone.make_aware(datetime.fromtimestamp(stat.st_mtime)),
        # Optional: add thumbnail for images
        "thumbnail": f"/media/thumbnails{path.relative_to(settings.MEDIA_ROOT)}" if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] else None,
    }
