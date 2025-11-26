import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


class LabirintStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        # Set the base path to the Samba mount
        kwargs["location"] = getattr(
            settings, "SAMBA_MOUNT_PATH", "/export/isilj/fenix2"
        )
        kwargs["base_url"] = (
            None  # Admin will use filer’s URLs; adjust if serving directly
        )
        super().__init__(*args, **kwargs)

    def path(self, name):
        # Ensure paths are relative to the Samba mount
        return os.path.join(self.location, name)

    def url(self, name):
        # Optional: If you need to serve files directly (e.g., for public access)
        # Adjust for your setup (e.g., Samba share URL or Nginx proxy)
        return f"/media/samba/{name}"


# Reference-only storage for /export/isilj/fenix2
fenix_storage = FileSystemStorage(
    location="/export/isilj/fenix2",
    base_url="/fenix2/",  # must be served by nginx/apache
)
