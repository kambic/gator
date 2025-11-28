"""
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelName
        fields = '__all__'

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return attrs
"""

from rest_framework import serializers

from apps.core.api.serializers import StreamSerializer
from ...models import *


class FileItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    is_dir = serializers.BooleanField()
    size = serializers.IntegerField(required=False, allow_null=True)
    modified = serializers.DateTimeField(required=False, allow_null=True)


class BreadcrumbItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()  # relative path
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        # Build full API URL for this breadcrumb level
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/files/{obj['path']}/".rstrip('/'))
        return f"/api/files/{obj['path']}/".rstrip('/')


class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['uri', 'stream_protocol']


class EdgeSerializer(serializers.ModelSerializer):
    streams = StreamSerializer(many=True)

    class Meta:
        model = Edge
        fields = ['pk', 'title', 'streams']


from rest_framework import serializers


class MoveItemSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.CharField())
    to = serializers.CharField()


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    path = serializers.CharField(required=False, default="")
