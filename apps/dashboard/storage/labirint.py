import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class LabirintStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs["location"] = getattr(
            settings, "SAMBA_MOUNT_PATH", "/export/isilj/fenix2"
        )
        kwargs["base_url"] = (
            None  # Admin will use filer’s URLs
        )
        super().__init__(*args, **kwargs)

    def path(self, name):
        # Ensure paths are relative to the Samba mount
        return os.path.join(self.location, name)

    def url(self, name):
        return f"/media/samba/{name}"
