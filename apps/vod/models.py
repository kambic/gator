from django.db import models
from django.db.models.functions import Coalesce
from django.utils.text import Truncator
from filer.fields.file import FilerFileField

from apps.dashboard.models import TimeStampedModel
from apps.users.models import User


class ProviderManager(models.Manager):
    def with_expired_count(self):
        return self.annotate(num_expired=Coalesce(models.Count("edgeware"), 0))


class Provider(models.Model):
    active = models.BooleanField(default=False)

    name = models.CharField(max_length=255, blank=True, null=True, editable=True)

    vidra_task = models.CharField(max_length=255, blank=True, null=True, editable=False)
    queue = models.CharField(max_length=255, blank=True, null=True, editable=False)

    objects = ProviderManager()

    class Meta:
        ordering = ["name"]  # Order by 'name' ascending by default

    @property
    def short_name(self):
        return Truncator(self.name).chars(15, truncate="...")


class Package(TimeStampedModel):
    name = models.CharField(max_length=255)
    original = FilerFileField(null=True, blank=True, related_name="originals", on_delete=models.SET_NULL)
    adi_xml = models.TextField(
        null=True,
        blank=True,
    )
    manifest = models.FileField(
        upload_to='manifests/',
        null=True,
        blank=True,
    )


class Video(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('adi_validated', 'ADI Validated'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('rejected', 'Rejected'),
        ('error', 'Error'),
    ]

    title = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    original_package = models.FileField(upload_to='packages/')
    mezzanine_video = models.FileField(upload_to='mezzanine/', blank=True)
    hevc_archive = models.FileField(upload_to='archive/hevc/', blank=True)
    dash_directory = models.CharField(max_length=255, blank=True)  # e.g. "dash/123/"

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_log = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title or f"Video {self.id}"
