from app import app_prod as celery_app

# ------------------------------------------------------------------------------
# Generic dispatcher for all legacy tasks
# ------------------------------------------------------------------------------
"""
from modern.legacy_tasks import encode_content

encode_content(
    "myname",
    123,
    "/tmp/video.mp4",
    ["h264_1080p", "h264_720p"],
    subtitles=["en", "de"],
    field_type="detect",
)

"""




def _dispatch(task_name: str, *, args=None, kwargs=None, queue=None):
    return celery_app.send_task(
        task_name,
        args=args or [],
        kwargs=kwargs or {},
        queue=queue,
    )


# ------------------------------------------------------------------------------
# Task wrappers
# ------------------------------------------------------------------------------

def process_trailer_worker(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.cronjob.process_trailer_worker",
        args=args,
        kwargs=kwargs,
        queue="default"
    )


def vpp_encrypt(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.drm.vpp_encrypt",
        args=args,
        kwargs=kwargs,
        queue="default"
    )


def adaptive_to_rtsp(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.encoding.adaptive_to_rtsp.adaptive_to_rtsp",
        args=args,
        kwargs=kwargs,
        queue="videoencoding"
    )


def encode_content(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.encoding.encode_content",
        args=args,
        kwargs=kwargs,
        queue="videoencoding"
    )


def encode_content_v2(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.encoding.encode_content_v2",
        args=args,
        kwargs=kwargs,
        queue="videoencoding"
    )


def process_trailer(*args, **kwargs):
    return _dispatch(
        "vydra.tasks.encoding.trailer.process_trailer",
        args=args,
        kwargs=kwargs,
        queue="videoencoding"
    )


# ------------------------------------------------------------------------------
# Ingest ADI tasks
# ------------------------------------------------------------------------------

def ingest_adi_hbo(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_hbo", args=args, kwargs=kwargs)

def ingest_adi_hbo_master(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_hbo_master", args=args, kwargs=kwargs)

def ingest_adi_hustler(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_hustler", args=args, kwargs=kwargs)

def ingest_adi_minimax(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_minimax", args=args, kwargs=kwargs)

def ingest_adi_pickbox(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_pickbox", args=args, kwargs=kwargs)

def ingest_adi_playboy(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_playboy", args=args, kwargs=kwargs)

def ingest_adi_vivid(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_vivid", args=args, kwargs=kwargs)

def ingest_adi_vubiquity(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_adi_vubiquity", args=args, kwargs=kwargs)


# ------------------------------------------------------------------------------
# Ingest package tasks
# ------------------------------------------------------------------------------

def ingest_package_alteka(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_alteka", args=args, kwargs=kwargs)

def ingest_package_babytv(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_babytv", args=args, kwargs=kwargs)

def ingest_package_blitz(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_blitz", args=args, kwargs=kwargs)

def ingest_package_cinestarpremiere(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_cinestarpremiere", args=args, kwargs=kwargs)

def ingest_package_curiositystream(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_curiositystream", args=args, kwargs=kwargs)

def ingest_package_dvk(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_dvk", args=args, kwargs=kwargs)

def ingest_package_epicdrama(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_epicdrama", args=args, kwargs=kwargs)

def ingest_package_kitchentv(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_kitchentv", args=args, kwargs=kwargs)

def ingest_package_moonbug(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_moonbug", args=args, kwargs=kwargs)

def ingest_package_natgeo(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_natgeo", args=args, kwargs=kwargs)

def ingest_package_planet_tv(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_planet_tv", args=args, kwargs=kwargs)

def ingest_package_sandbox(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_sandbox", args=args, kwargs=kwargs)

def ingest_package_viasat(*args, **kwargs):
    return _dispatch("vydra.tasks.ingest_package_viasat", args=args, kwargs=kwargs)
