import os
import tarfile
import tempfile
import subprocess
from pathlib import Path
from lxml import etree
from celery import shared_task, group
from django.conf import settings
from .models import Video

# Schema paths
BASE_DIR = Path(settings.BASE_DIR)
SCHEMA_DIR = BASE_DIR / 'vod' / 'schema'
GENERIC_XSD = SCHEMA_DIR / 'generic' / 'ADI_1.1.xsd'

# Provider map
PROVIDER_XSD_MAP = {
    'comcast': SCHEMA_DIR / 'providers' / 'comcast' / 'Comcast_ADI_1.13.xsd',
    'charter': SCHEMA_DIR / 'providers' / 'charter' / 'Charter_ADI_1.12.xsd',
    'cox': SCHEMA_DIR / 'providers' / 'cox' / 'Cox_ADI_1.11.xsd',
}

_schema_cache = {}

import logging

logger = logging.getLogger(__name__)


def _load_schema(path):
    if not path.exists():
        return None
    if path not in _schema_cache:
        schema_root = etree.parse(str(path))
        _schema_cache[path] = etree.XMLSchema(schema_root)
    return _schema_cache[path]


def find_adi_in_tar(tar):
    for member in tar.getmembers():
        if member.isfile() and member.name.lower().endswith(('adi.xml', 'package.xml')):
            return member
    return None


def find_video_file(extract_dir):
    for ext in ['.mp4', '.mpg', '.mpeg', '.mov', '.mxf']:
        for f in Path(extract_dir).rglob(f'*{ext}'):
            if f.is_file():
                return f
    return None


@shared_task(bind=True, max_retries=3)
def process_vod_package(self, video_id):
    video = Video.objects.get(id=video_id)
    package_path = video.original_package.path

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # 1. Extract tar
            with tarfile.open(package_path, 'r:*') as tar:
                tar.extractall(path=tmpdir)

                # 2. Find and validate ADI.xml
                adi_member = find_adi_in_tar(tar)
                if not adi_member:
                    raise Exception("ADI.xml not found in package")

                tar.extract(adi_member, path=tmpdir)
                adi_path = tmp_path / adi_member.name
                errors, provider, root = validate_adi(adi_path)

                if errors:
                    video.status = 'rejected'
                    video.processing_log = str(errors)
                    video.metadata = {"provider": provider, "validation_errors": errors}
                    video.save()
                    return

                # 3. Find mezzanine video
                mezz_file = find_video_file(tmpdir)
                if not mezz_file:
                    raise Exception("No supported video file found")

                # Save mezzanine
                dest = settings.MEDIA_ROOT / 'mezzanine' / f"{video.id}{mezz_file.suffix}"
                dest.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(['cp', str(mezz_file), str(dest)], check=True)
                video.mezzanine_video = f"mezzanine/{video.id}{mezz_file.suffix}"

                # Extract title from ADI
                title = root.findtext('.//Title') or root.findtext('.//AMS/Title') or f"Asset {video.id}"
                video.title = title[:255]
                video.metadata = {"provider": provider, "asset_id": root.findtext('.//AMS/Asset_ID')}
                video.status = 'adi_validated'
                video.save()

                # 4. Chain to transcoding
                chain = archive_to_hevc.s(video.id) | transcode_to_dash.s(video.id)
                chain.delay()

    except Exception as exc:
        video.status = 'error'
        video.processing_log = str(exc)
        video.save()
        raise self.retry(exc=exc, countdown=60)


def validate_adi(adi_path):
    logger.info(f"Validating ADI: {adi_path}")

    tree = etree.parse(str(adi_path))
    root = tree.getroot()

    # Detect provider
    provider = root.findtext('.//Provider') or ''
    provider = provider.strip().lower()
    logger.info(f"Detected provider: {provider}")

    errors = []

    # Generic validation
    schema = _load_schema(GENERIC_XSD)
    logger.info(f"Using generic schema: {GENERIC_XSD}")
    if schema:
        try:
            schema.assertValid(tree)
        except etree.DocumentInvalid as e:
            errors.append({"type": "generic", "errors": [err.message for err in e.error_log]})

    # Provider-specific
    prov_schema_path = PROVIDER_XSD_MAP.get(provider)
    logger.info(f"Using provider schema: {prov_schema_path}")
    if prov_schema_path and prov_schema_path.exists():
        schema = _load_schema(prov_schema_path)
        if schema:
            try:
                schema.assertValid(tree)
            except etree.DocumentInvalid as e:
                errors.append({"type": f"provider_{provider}", "errors": [err.message for err in e.error_log]})
    return errors, provider, root


@shared_task
def archive_to_hevc(video_id):
    video = Video.objects.get(id=video_id)
    input_path = video.mezzanine_video.path
    output_path = settings.MEDIA_ROOT / 'archive' / 'hevc' / f"{video_id}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = ['ffmpeg', '-i', input_path, '-c:v', 'libx265', '-preset', 'slow', '-crf', '23', '-c:a', 'copy', '-y', str(output_path)]
    subprocess.run(cmd, check=True)
    video.hevc_archive = f"archive/hevc/{video_id}.mp4"
    video.save()


@shared_task
def transcode_to_dash(video_id):
    video = Video.objects.get(id=video_id)
    input_path = video.mezzanine_video.path
    dash_dir = settings.MEDIA_ROOT / 'dash' / str(video_id)
    dash_dir.mkdir(parents=True, exist_ok=True)

    resolutions = [
        ("426x240", "400k", "240p"),
        ("640x360", "800k", "360p"),
        ("854x480", "1500k", "480p"),
        ("1280x720", "3500k", "720p"),
        ("1920x1080", "6000k", "1080p"),
    ]

    frag_files = []
    for w_h, bitrate, label in resolutions:
        frag = dash_dir / f"output_{label}.mp4"
        cmd = ['ffmpeg', '-i', input_path, '-vf', f"scale={w_h}", '-c:v', 'libx264', '-b:v', bitrate, '-c:a', 'aac', '-b:a', '128k', '-f', 'mp4', '-y', str(frag)]
        subprocess.run(cmd, check=True)
        frag_files.append(str(frag))

    # DASH packaging with Bento4
    mp4dash_cmd = ['mp4dash', '-o', str(dash_dir), '--profile=on-demand'] + frag_files
    subprocess.run(mp4dash_cmd, check=True)

    video.dash_directory = f"dash/{video_id}/"
    video.status = 'ready'
    video.save()
