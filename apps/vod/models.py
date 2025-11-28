from pathlib import Path

from django.db import models
from django.db.models.functions import Coalesce
from django.utils.text import Truncator
from filer.fields.file import FilerFileField

from apps.dashboard.models import TimeStampedModel
from apps.users.models import User
from vidra_kit.adi import ADIParser
from vidra_kit.adi.parser import ADIParseError
from vidra_kit.adi.validator import ADIValidatorConfig, ADIValidator

from vidra_kit import logger


class ProviderManager(models.Manager):
    def with_expired_count(self):
        return self.annotate(num_expired=Coalesce(models.Count("edgeware"), 0))


class Provider(models.Model):
    active = models.BooleanField(default=False)

    name = models.CharField(max_length=255, blank=True, null=True, editable=True)

    vidra_task = models.CharField(max_length=255, blank=True, null=True, editable=True)
    queue = models.CharField(max_length=255, blank=True, null=True, editable=True)

    objects = ProviderManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=['name', 'vidra_task', 'queue'], name="unique_provider_task"),
        ]

    @property
    def short_name(self):
        return Truncator(self.name).chars(15, truncate="...")

    def __str__(self):
        return self.short_name


class Package(TimeStampedModel):
    name = models.CharField(max_length=255)
    original = FilerFileField(null=True, blank=True, related_name="originals", on_delete=models.SET_NULL)

    manifest = models.FileField(
        upload_to='manifests/',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    @property
    def adi_xml(self):
        with self.manifest.open() as f:
            content = f.read()
        return content.decode()

    def validate_manifest(self):
        config = ADIValidatorConfig(
            xsd_paths=[
                Path("/home/e-kambicr/neo/alligator/vidra-kit/src/vidra_kit/adi/schemas/adi_movie.xsd"),
            ]
        )

        validator = ADIValidator(config=config)
        result = validator.validate(str(self.manifest.file))

        logger.info(f"Manifest validation result: {result.success}")

    def extract_metadata(self):
        # 1. Initialize the parser
        try:
            parser = ADIParser(xml_path=str(self.manifest.file))

            # 2. Execute the parse method
            meta = parser.parse()

            # 3. Use the structured data
            logger.info("## Global Metadata (Title, Provider ID, etc.)")
            logger.info(meta.metadata)
            logger.info("\n## Asset List")
            logger.info(meta.assets)

            # Example: Accessing the first Asset's Title
            if meta.assets:
                first_asset_title = meta.assets[0].metadata.get('Title')
                logger.info(f"\nFirst Asset Title: {first_asset_title}")

        except ADIParseError as e:
            logger.info(f"Parsing failed: {e}")


class Video(TimeStampedModel):
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
    original_package = models.FileField(upload_to='packages/', blank=True)
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


class ExpiredManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(mtcms_prod=True)


class Edge(models.Model):
    class Status(models.TextChoices):
        ERROR = "error", "ERROR"
        DONE = "done", "SUCCESS"

    content_id = models.CharField(max_length=255, null=True, unique=True)
    title = models.CharField(max_length=255, null=True)
    creation_time = models.DateTimeField(null=True)
    modification_time = models.DateTimeField(null=True)

    status = models.CharField(max_length=10, choices=Status, null=True)

    playable = models.BooleanField(default=False)
    content_duration_ms = models.IntegerField(null=True)

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True)

    objects = models.Manager()  # The default manager.
    expired_objects = ExpiredManager()

    def __str__(self) -> str:
        return self.title

    @property
    def short_name(self):
        return Truncator(self.title).chars(15, truncate="...")


class Stream(models.Model):
    PROTOCOL = [
        ("hls", "hls"),
        ("dash", "dash"),
        ("mss", "mss"),
    ]
    edge = models.ForeignKey(Edge, on_delete=models.CASCADE, null=True, related_name="streams")
    stream_protocol = models.CharField(max_length=4, choices=PROTOCOL)
    uri = models.URLField(max_length=512)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["edge", "stream_protocol"], name="unq_edge_proto")]

    def __str__(self):
        return f"[{self.stream_protocol}] {self.edge.title}"
