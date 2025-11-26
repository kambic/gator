# from django_celery_results.models import TaskResult
from rest_framework import serializers



class VideoSerializer(serializers.Serializer):
    type = serializers.CharField()
    info = serializers.CharField()


class SubtitleSerializer(serializers.Serializer):
    type = serializers.CharField()
    info = serializers.CharField()


class JobSerializer(serializers.Serializer):
    name = serializers.CharField()
    content_id = serializers.CharField(allow_null=True, required=False)
    video = VideoSerializer()
    profiles = serializers.ListField(child=serializers.CharField())
    adaptive_dest = serializers.CharField()
    seconds = serializers.IntegerField(allow_null=True, required=False)
    ott_realm = serializers.CharField()
    drm_required = serializers.BooleanField()
    audio = serializers.CharField(allow_null=True, required=False)
    subtitles = SubtitleSerializer(allow_null=True, required=False)
