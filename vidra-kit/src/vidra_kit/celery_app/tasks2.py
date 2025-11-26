"""
ping.py
Modern wrapper layer for calling legacy Celery tasks by name.

- No direct imports from legacy code.
- Explicit signatures where known.
- Dispatch through a single safe method.
- All tasks kept in one clear interface module.
"""

from celery import current_app as celery_app

# ---------------------------------------------------------------------------
# Generic dispatcher
# ---------------------------------------------------------------------------

def _dispatch(task_name: str, *, args=None, kwargs=None, queue=None):
    """Unified Celery task dispatcher for legacy tasks."""
    return celery_app.send_task(
        task_name,
        args=args or [],
        kwargs=kwargs or {},
        queue=queue,
    )


# ---------------------------------------------------------------------------
# Encoding Tasks
# ---------------------------------------------------------------------------

def encode_content(
    name: str,
    content_id: int,
    video: str,
    profiles: list[str],
    audio: list[str] | None = None,
    subtitles: list[str] | None = None,
    log: dict | None = None,
    seconds: int | None = None,
    field_type: str = "detect",
    normalize: str = "loudnorm_truepeak",
    drm_required: bool = True,
    **kwargs
):
    return _dispatch(
        "vydra.tasks.encoding.encode_content",
        args=[name, content_id, video, profiles],
        kwargs={
            "audio": audio,
            "subtitles": subtitles,
            "log": log,
            "seconds": seconds,
            "field_type": field_type,
            "normalize": normalize,
            "drm_required": drm_required,
            **kwargs,
        },
        queue="videoencoding",
    )


def encode_content_v2(
    name: str,
    content_id: int,
    video: str,
    profiles: list[str],
    audio: list[str] | None = None,
    subtitles: list[str] | None = None,
    log: dict | None = None,
    seconds: int | None = None,
    field_type: str = "detect",
    normalize: str = "loudnorm_truepeak",
    drm_required: bool = True,
    **kwargs
):
    return _dispatch(
        "vydra.tasks.encoding.encode_content_v2",
        args=[name, content_id, video, profiles],
        kwargs={
            "audio": audio,
            "subtitles": subtitles,
            "log": log,
            "seconds": seconds,
            "field_type": field_type,
            "normalize": normalize,
            "drm_required": drm_required,
            **kwargs,
        },
        queue="videoencoding",
    )


def adaptive_to_rtsp(
    content_id: int,
    source_url: str,
    profile: str,
    audio_tracks: list[str] | None = None,
    subtitles: list[str] | None = None,
    **kwargs
):
    return _dispatch(
        "vydra.tasks.encoding.adaptive_to_rtsp.adaptive_to_rtsp",
        args=[content_id, source_url, profile],
        kwargs={
            "audio_tracks": audio_tracks,
            "subtitles": subtitles,
            **kwargs,
        },
        queue="videoencoding",
    )


def process_trailer(
    content_id: int,
    source_file: str,
    profiles: list[str],
    **kwargs
):
    return _dispatch(
        "vydra.tasks.encoding.trailer.process_trailer",
        args=[content_id, source_file, profiles],
        kwargs=kwargs,
        queue="videoencoding",
    )


# ---------------------------------------------------------------------------
# DRM Tasks
# ---------------------------------------------------------------------------

def vpp_encrypt(
    content_id: int,
    input_file: str,
    output_file: str,
    key_id: str,
    key: str,
    widevine: bool = True,
    playready: bool = True,
    fairplay: bool = False,
    **kwargs
):
    return _dispatch(
        "vydra.tasks.drm.vpp_encrypt",
        args=[content_id, input_file, output_file],
        kwargs={
            "key_id": key_id,
            "key": key,
            "widevine": widevine,
            "playready": playready,
            "fairplay": fairplay,
            **kwargs,
        },
    )


# ---------------------------------------------------------------------------
# Cron Tasks
# ---------------------------------------------------------------------------

def process_trailer_worker():
    return _dispatch(
        "vydra.tasks.cronjob.process_trailer_worker",
        args=[],
        kwargs={},
    )


# ---------------------------------------------------------------------------
# ADI Ingest Tasks (explicit signature from your code)
# ---------------------------------------------------------------------------

def ingest_adi_hbo(adi):
    return _dispatch(
        "vydra.tasks.ingest_adi_hbo",
        args=[adi],
        kwargs={},
    )


# The rest follow the same pattern until you provide their exact signatures.

def ingest_adi_hbo_master(adi):
    return _dispatch("vydra.tasks.ingest_adi_hbo_master", args=[adi], kwargs={})

def ingest_adi_hustler(adi):
    return _dispatch("vydra.tasks.ingest_adi_hustler", args=[adi], kwargs={})

def ingest_adi_minimax(adi):
    return _dispatch("vydra.tasks.ingest_adi_minimax", args=[adi], kwargs={})

def ingest_adi_pickbox(adi):
    return _dispatch("vydra.tasks.ingest_adi_pickbox", args=[adi], kwargs={})

def ingest_adi_playboy(adi):
    return _dispatch("vydra.tasks.ingest_adi_playboy", args=[adi], kwargs={})

def ingest_adi_vivid(adi):
    return _dispatch("vydra.tasks.ingest_adi_vivid", args=[adi], kwargs={})

def ingest_adi_vubiquity(adi):
    return _dispatch("vydra.tasks.ingest_adi_vubiquity", args=[adi], kwargs={})


# ---------------------------------------------------------------------------
# Package Ingest Tasks
# ---------------------------------------------------------------------------

def ingest_package_alteka(adi):
    return _dispatch("vydra.tasks.ingest_package_alteka", args=[adi], kwargs={})

def ingest_package_babytv(adi):
    return _dispatch("vydra.tasks.ingest_package_babytv", args=[adi], kwargs={})

def ingest_package_blitz(adi):
    return _dispatch("vydra.tasks.ingest_package_blitz", args=[adi], kwargs={})

def ingest_package_cinestarpremiere(adi):
    return _dispatch("vydra.tasks.ingest_package_cinestarpremiere", args=[adi], kwargs={})

def ingest_package_curiositystream(adi):
    return _dispatch("vydra.tasks.ingest_package_curiositystream", args=[adi], kwargs={})

def ingest_package_dvk(adi):
    return _dispatch("vydra.tasks.ingest_package_dvk", args=[adi], kwargs={})

def ingest_package_epicdrama(adi):
    return _dispatch("vydra.tasks.ingest_package_epicdrama", args=[adi], kwargs={})

def ingest_package_kitchentv(adi):
    return _dispatch("vydra.tasks.ingest_package_kitchentv", args=[adi], kwargs={})

def ingest_package_moonbug(adi):
    return _dispatch("vydra.tasks.ingest_package_moonbug", args=[adi], kwargs={})

def ingest_package_natgeo(adi):
    return _dispatch("vydra.tasks.ingest_package_natgeo", args=[adi], kwargs={})

def ingest_package_planet_tv(adi):
    return _dispatch("vydra.tasks.ingest_package_planet_tv", args=[adi], kwargs={})

def ingest_package_sandbox(adi):
    return _dispatch("vydra.tasks.ingest_package_sandbox", args=[adi], kwargs={})

def ingest_package_viasat(adi):
    return _dispatch("vydra.tasks.ingest_package_viasat", args=[adi], kwargs={})
