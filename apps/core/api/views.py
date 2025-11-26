
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.dashboard.models import Provider, Edgeware
from .serializers import ProviderSerializer, EdgewareSerializer


# views.py
class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.with_expired_count()
    serializer_class = ProviderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['vidra_task', 'queue', 'user__username', 'user__email']
    ordering_fields = ['user__username', 'user__email', 'vidra_task', 'queue', 'num_expired']
    ordering = ['user__username']  # default sort

class EdgewareViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EdgewareSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title', 'ew_id', 'offer_id', 'provider__user__username']
    ordering_fields = ['ingested', 'expired', 'title', 'status']
    ordering = '-ingested'

    def get_queryset(self):
        qs = Edgeware.objects.select_related('provider__user').prefetch_related('stream_set')

        # Custom filters
        status = self.request.query_params.get('status')
        encoder = self.request.query_params.get('encoder')
        provider = self.request.query_params.get('provider')

        if status:
            qs = qs.filter(status=status)
        if encoder:
            qs = qs.filter(encoder=encoder)
        if provider:
            qs = qs.filter(provider_id=provider)

        return qs
