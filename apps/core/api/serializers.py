from rest_framework import serializers
from ...dashboard.models import Provider, Edgeware, Stream
from ...users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # whatever fields you want

class ProviderSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(source='user.username', read_only=True)
    user = UserSerializer(read_only=True)
    num_expired = serializers.ReadOnlyField()

    class Meta:
        model = Provider
        fields = ['id', 'user', 'vidra_task', 'queue', 'num_expired']



class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['type', 'uri']

class EdgewareSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    encoder_display = serializers.CharField(source='get_encoder_display', read_only=True)
    duration = serializers.SerializerMethodField()
    streams = StreamSerializer(many=True, read_only=True)

    class Meta:
        model = Edgeware
        fields = [
            'id', 'title', 'ew_id', 'offer_id', 'status', 'status_display',
            'encoder_display', 'ingested', 'expired', 'playable',
            'provider', 'provider_name', 'duration', 'streams'
        ]

    def get_duration(self, obj):
        return obj.content_duration if hasattr(obj, 'content_duration') else None

class FileItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    is_dir = serializers.BooleanField()
    size = serializers.IntegerField(required=False)
    modified = serializers.DateTimeField(required=False)
