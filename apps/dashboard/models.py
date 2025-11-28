import json
import structlog as logging
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone as dj_tz
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from vidra_kit.backends import AtemeApi
from ..utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class ProviderManager(models.Manager):
    def with_expired_count(self):
        return self.annotate(num_expired=Coalesce(models.Count("edgeware"), 0))


class Provider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(default=False)
    use_staging_db = models.BooleanField(default=True)
    enable_drm = models.BooleanField(default=True)

    default_active_tv = models.BooleanField(default=True)
    default_active_web = models.BooleanField(default=True)
    default_active_mobile = models.BooleanField(default=True)
    default_active_lte = models.BooleanField(default=True)
    catalog_name = models.CharField(max_length=255, blank=True, null=True, editable=True)

    vidra_task = models.CharField(max_length=255, blank=True, null=True, editable=False)
    queue = models.CharField(max_length=255, blank=True, null=True, editable=False)
    provider_fs = models.CharField(max_length=255, blank=True, null=True, editable=False)

    objects = ProviderManager()

    class Meta:
        ordering = ["user__username"]  # Order by 'name' ascending by default

    @property
    def short_name(self):
        return Truncator(self.user.name).chars(15, truncate="...")


class ExpiredManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mtcms_prod=True)


class Edgeware(models.Model):
    class Status(models.TextChoices):
        FTP_UPLOAD = "ftp_done", "FTP UPLOADED"
        FTP_ERROR = "ftp_error", "FTP ERROR"
        EW_ERROR = "ew_error", "EW ERROR"
        EW_SUCCESS = "done", "EW SUCCESS"
        EW_PENDIND = "ew_pending", "EW PENDING"

        ETL = "etl", "Collected from log"

    class Encoder(models.TextChoices):
        ATEME = "ateme", "ATEME"
        VIDRA = "vidra", "VIDRA"

    created = models.DateTimeField(null=True)
    modified = models.DateTimeField(null=True)
    ingested = models.DateTimeField(null=True, help_text='vidra ingested')
    expired = models.DateTimeField(null=True, help_text='mtcms expired offer')
    ew_id = models.CharField(max_length=255, null=True)
    offer_id = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)

    # stream_url = models.CharField(max_length=255, null=True)
    host = models.CharField(max_length=32, default="")
    celery_id = models.CharField(max_length=255, unique=True, null=True)
    status = models.CharField(max_length=10, choices=Status, null=True)
    encoder = models.CharField(max_length=5, choices=Encoder, default=Encoder.ATEME)

    ftp_dir = models.CharField(max_length=255, default="")
    ew_dump_loaded = models.BooleanField(default=False)
    mtcms_stag = models.BooleanField(default=False)
    mtcms_prod = models.BooleanField(default=False)
    playable = models.BooleanField(default=False)
    content_duration_ms = models.IntegerField(null=True)

    msg = models.JSONField(default=dict)

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True)

    objects = models.Manager()  # The default manager.
    expired_objects = ExpiredManager()

    def __str__(self) -> str:
        return self.title

    @property
    def short_name(self):
        return Truncator(self.title).chars(15, truncate="...")

    @property
    def content_duration(self):
        if self.content_duration_ms:
            return f"{timedelta(milliseconds=int(self.content_duration_ms)).total_seconds() / 60 : .2f} minutes"


class ExpiredEdgeware(Edgeware):
    objects = ExpiredManager()

    class Meta:
        proxy = True
        ordering = ['expired']  # Optional: override ordering

    def __str__(self):
        return f"[EXPIRED] {self.title}"


class Stream(models.Model):
    TYPE_CHOICES = [
        ("hls", "hls"),
        ("dash", "dash"),
        ("mss", "mss"),
    ]
    edge = models.ForeignKey(Edgeware, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    uri = models.URLField(max_length=512)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["edge", "type"], name="unq_edge_stream")]

    def __str__(self):
        return f"[{self.type}] {self.edge.title}"


class VidraJob(TimeStampedModel):
    class Env(models.TextChoices):
        STAG = "stag", "Staging"
        PROD = "prod", "Production"

    env = models.CharField(max_length=4, choices=Env.choices, default=Env.STAG, null=True)
    name = models.CharField(max_length=128, null=True)
    uuid = models.CharField(max_length=128, null=True)
    state = models.CharField(max_length=16, null=True)
    hostname = models.CharField(max_length=32, null=True)
    worker = models.CharField(max_length=32, null=True)

    args = models.JSONField(null=True)
    kwargs = models.JSONField(null=True)
    meta = models.JSONField(null=True, default=dict)
    result = models.JSONField(null=True)
    exception = models.TextField(null=True)

    received = models.DateTimeField(null=True, blank=True, editable=False)
    started = models.DateTimeField(null=True, blank=True, editable=False)
    succeeded = models.DateTimeField(null=True, blank=True, editable=False)
    timestamp = models.DateTimeField(null=True, blank=True, editable=False)
    runtime = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f'{self.name}'

    # def get_absolute_url(self):
    #     return reverse("dashboard:task_detail_ui", kwargs={"task_id": self.uuid})


class AtemeJob(TimeStampedModel):
    name = models.CharField(max_length=128, editable=False)
    asset = models.ForeignKey('FileEntry', on_delete=models.CASCADE, null=True)
    ateme_id = models.CharField(max_length=128, null=True, editable=False)
    payload = models.JSONField(default=dict, editable=False)
    state = models.CharField(max_length=16, default="created")
    priority = models.SmallIntegerField(default=1)

    output = models.FilePathField(
        null=True,
        path="/export/isilj/encode-ateme/output",
        recursive=True,
        match=".*.mpd$",
    )

    job_details = models.JSONField(default=dict)

    ateme_api = AtemeApi()

    def __str__(self):
        return self.ateme_id

    def collect_job_details(self):
        stat = self.ateme_api.get_job(self.ateme_id)
        self.job_details = stat
        self.save()


class AtemeJobEvent(TimeStampedModel):
    class Status(models.TextChoices):
        FAILED = "inerror", _("Failed")
        STARTED = "running", _("Started")
        SUCCESS = "completed", _("Success")

    ateme_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=Status.choices)
    payload = models.JSONField(default=dict)
    job = models.ForeignKey(AtemeJob, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"[{self.status}] - {self.name}"

    @classmethod
    def new_event(cls, data):
        logger.info(f"New Ateme event: {data}")

        job, created = AtemeJob.objects.get_or_create(ateme_id=data["id"])
        if created:
            job.name = data["name"]

        job.state = data["status"]
        job.save()

        cls.objects.create(
            ateme_id=data["id"],
            name=data["name"],
            status=data["status"],
            payload=data,
            job=job,
        )

        if job.state == "completed":
            job.collect_job_details()


class FileEntry(MPTTModel):
    TYPE_CHOICES = [
        ("dir", "Directory"),
        ("file", "File"),
    ]

    name = models.CharField(max_length=255)
    path = models.TextField(unique=True)
    entry_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    size = models.BigIntegerField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)
    parent = TreeForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return f"{self.entry_type.upper()}: {self.path}"


class Packet(TimeStampedModel):
    class Status(models.TextChoices):
        DELIVERED = "upload", "Delivered"
        ENQUEUED = "enqueued", "Enqueued"
        PROCESSING = "processing", "Processing"
        FAILED = "failed", "Failed"

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="packets", editable=False)
    title = models.CharField(max_length=255, editable=False)
    delivery_time = models.DateTimeField(blank=True, null=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DELIVERED, editable=False)
    file = models.FilePathField(path="/export/isilj/fenix2", match=".*tar", recursive=True, editable=True, unique=True, max_length=512)
    size = models.BigIntegerField(null=True, blank=True)

    @property
    def collect_file_stats(self):
        """
        Collect metadata from a file using pathlib.Path and return as a dictionary.
        Timestamps are converted to timezone-aware datetime objects (UTC).

        Returns:
            dict: Dictionary containing file metadata.
        """
        try:
            path = Path(self.file)
            stats = path.stat()

            tz = timezone.get_current_timezone()

            return {
                "name": path.name,
                "absolute_path": str(path.absolute()),
                "size_bytes": stats.st_size,
                "created_at": datetime.fromtimestamp(stats.st_ctime, tz=tz),
                "modified_at": datetime.fromtimestamp(stats.st_mtime, tz=tz),
                "accessed_at": datetime.fromtimestamp(stats.st_atime, tz=tz),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "mode": stats.st_mode,
                "owner_id": stats.st_uid,
                "group_id": stats.st_gid,
            }
        except FileNotFoundError:
            return {"error": f"File not found: {self.file}"}
        except PermissionError:
            return {"error": f"Permission denied: {self.file}"}
        except Exception as e:
            return {"error": f"Error accessing file {self.file}: {str(e)}"}

    def move_to_vidra_ftp_folder(self):
        """
        Moves the file to a destination folder and updates file.
        """
        file = Path(self.file)
        dest = self.provider.media_cloud / file.name

        # Path(dest).mkdir(parents=True, exist_ok=True)
        try:

            shutil.move(file, dest)
            self.file = dest
            self.save(update_fields=["file"])
        except (shutil.Error, OSError) as e:
            logger.error(f"Failed to copy file {file} to {dest}: {e}")
            raise

    @property
    def task_payload(self) -> dict:
        """Build FTP payload for the given file."""
        file = Path(self.file)
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        return {
            "type": "ftp",
            "host": "bpl-phoenix3.ts.telekom.si",
            "port": 2121,
            "passive": True,
            "folder": "/queue/",
            "filesize": file.stat().st_size,
            "filename": file.name,
            "username": self.provider.ftp_user,
            "password": self.provider.ftp_password,
        }


class SFTPGoEvent(models.Model):
    # Core event info
    event = models.CharField(max_length=50, db_index=True, help_text="upload, download, delete, rename, etc.")
    username = models.CharField(max_length=255, db_index=True)
    ip = models.GenericIPAddressField(db_index=True)
    role = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=100, blank=True, null=True, help_text="SFTPGo internal user ID")

    # Protocol & paths
    protocol = models.CharField(max_length=20)  # SFTP, FTP, WebDAV, HTTP, etc.
    path = models.TextField(help_text="Full filesystem path on the server")
    virtual_path = models.TextField(help_text="Path as seen by the user")

    # File info
    file_size = models.BigIntegerField(default=0, help_text="Size in bytes")
    object_name = models.TextField(blank=True, null=True, help_text="Usually the filename")
    object_type = models.CharField(max_length=50, blank=True, null=True)

    # Status & timing
    status = models.PositiveSmallIntegerField(choices=((1, "Success"), (2, "Error")), db_index=True)
    timestamp = models.BigIntegerField(help_text="SFTPGo nanosecond timestamp (Unix epoch * 1e9 + ns)")
    date = models.DateTimeField(db_index=True, help_text="Human-readable ISO datetime from SFTPGo")
    elapsed = models.PositiveIntegerField(blank=True, null=True, help_text="Operation time in milliseconds")

    # Flexible fields
    object_data = models.JSONField(default=dict, blank=True, help_text="Extra object data (user/folder JSON when applicable)")
    error = models.TextField(blank=True, null=True)

    # Auto-filled
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "SFTPGo Event"
        verbose_name_plural = "SFTPGo Events"
        indexes = [
            models.Index(fields=['username', 'event']),
            models.Index(fields=['date']),
            models.Index(fields=['protocol']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.event.upper()} by {self.username} @ {self.date}"

    # Helper: convert SFTPGo nanosecond timestamp → Python datetime
    @property
    def timestamp_datetime(self):
        from datetime import datetime, timedelta

        seconds = self.timestamp // 1_000_000_000
        nanoseconds = self.timestamp % 1_000_000_000
        return datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(microseconds=nanoseconds // 1000)

    # Optional: save from webhook payload directly
    @classmethod
    def create_from_webhook(cls, payload: dict):
        # Handle empty strings that should be null
        data = payload.copy()
        if data.get("object_data") == "{}":
            data["object_data"] = {}

        elif isinstance(data.get("object_data"), str):
            data["object_data"] = json.loads(data["object_data"])

        # Parse date if not already datetime
        if isinstance(data.get("date"), str):
            # Parse as UTC, then convert to Ljubljana time
            ts = data["date"]

            # Parse string and mark it as UTC
            utc_dt = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)

            # Convert to your Django TIME_ZONE (Europe/Ljubljana)
            local_dt = dj_tz.localtime(utc_dt)

            data["date"] = local_dt

        return cls.objects.create(**data)


#
#
# class RemoteFile(models.Model):
#     uri = models.CharField(
#         max_length=1500,
#         unique=True,
#         db_index=True,
#         help_text="Full ftp:// URI, e.g. ftp://user:pass@host:21/path/file.txt"
#     )
#
#     name = models.CharField(max_length=255)
#     size = models.BigIntegerField(null=True, blank=True)
#     modified = models.DateTimeField(null=True, blank=True)
#
#     first_seen = models.DateTimeField(auto_now_add=True)
#     last_seen = models.DateTimeField(auto_now=True)
#     scan_count = models.PositiveIntegerField(default=1)
#
#     class Meta:
#         ordering = ["-last_seen"]
#         indexes = [
#             models.Index(fields=["last_seen"]),
#             models.Index(fields=["size"]),
#         ]
#
#     def __str__(self):
#         return self.uri
