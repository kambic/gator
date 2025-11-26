from django.apps import AppConfig


class VideoTranscodingConfig(AppConfig):
    name = "apps.video_transcoding"
    verbose_name = "Video Transcoding"

    # def ready(self) -> None:
    # __import__("video_transcoding.signals")
