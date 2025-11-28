from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, UpdateView, ListView
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FileNode
from ..dashboard.models import Provider, Edgeware


# Create your views here.

import os
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from ..vod.api.v1.serializers import FileItemSerializer

BASE_DIR = "/export"


class ShakaPlayer(TemplateView):
    template_name = 'core/shaka.html'


def index(request):
    return render(request, "core/index.html")


def file_explorer(request):
    # Root nodes (parent is null)
    roots = FileNode.objects.filter(parent=None)
    return render(request, "core/file_manager.html", {"roots": roots})


def htmx_load_children(request, node_id):
    node = get_object_or_404(FileNode, id=node_id)
    return render(request, "core/partials/_children.html", {"node": node})


@csrf_exempt
def upload_file(request):
    rel_path = request.POST.get("path", "")
    abs_path = os.path.join(BASE_DIR, rel_path)

    file = request.FILES["file"]
    os.makedirs(abs_path, exist_ok=True)

    with open(os.path.join(abs_path, file.name), "wb+") as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return JsonResponse({"status": "ok"})


class ProviderListView(TemplateView):
    template_name = "core/providers_list.html"


class ProviderDetailView(LoginRequiredMixin, DetailView):
    model = Provider
    template_name = 'core/provider_detail.html'
    context_object_name = 'provider'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return Provider.objects.with_expired_count().select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Provider: {self.object.user.username}"
        return context


# UPDATE
class ProviderUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Provider
    template_name = 'core/provider_form.html'
    fields = ['vidra_task', 'queue']
    success_message = "Provider updated successfully!"
    success_url = reverse_lazy('core:providers-list')


class EdgewareListView(LoginRequiredMixin, ListView):
    model = Edgeware
    template_name = 'core/edgeware_list.html'
    context_object_name = 'edgewares'
    paginate_by = 50

    def get_queryset(self):
        qs = Edgeware.objects.select_related('provider__user').prefetch_related('stream_set')

        # Filters
        if status := self.request.GET.get('status'):
            qs = qs.filter(status=status)
        if encoder := self.request.GET.get('encoder'):
            qs = qs.filter(encoder=encoder)
        if provider_id := self.request.GET.get('provider'):
            qs = qs.filter(provider_id=provider_id)
        if search := self.request.GET.get('search'):
            qs = qs.filter(Q(title__icontains=search) | Q(ew_id__icontains=search) | Q(offer_id__icontains=search))

        return qs.order_by('-ingested')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = Provider.objects.all()
        from django.db.models import Count, Case, When, IntegerField, Q

        context['aggregate'] = Edgeware.objects.aggregate(
            success=Count(Case(When(status='done', then=1), output_field=IntegerField())),
            pending=Count(Case(When(status='ew_pending', then=1), output_field=IntegerField())),
            errors=Count(Case(When(status__contains='error', then=1), output_field=IntegerField())),
            playable=Count(Case(When(playable=True, then=1), output_field=IntegerField())),
            expired=Count(Case(When(expired__isnull=False, then=1), output_field=IntegerField())),
        )

        # Stats
        all = Edgeware.objects.all()
        context['stats'] = {
            'done': all.filter(status='done').count(),
            'pending': all.filter(status='ew_pending').count(),
            'errors': all.filter(status__in=['ew_error', 'ftp_error']).count(),
            'playable': all.filter(playable=True).count(),
            'expired': all.filter(expired__isnull=False).count(),
        }

        # Default to 0 if no rows match

        return context


class FileAPIView(APIView):
    """
    REST API for browsing, uploading, and deleting files.
    """

    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        rel_path = request.query_params.get('path', '')
        abs_path = os.path.join(BASE_DIR, rel_path)

        if not os.path.exists(abs_path):
            return Response({'error': 'Path not found'}, status=status.HTTP_404_NOT_FOUND)

        items = []
        for name in os.listdir(abs_path):
            full_path = os.path.join(abs_path, name)
            stat = os.stat(full_path)
            items.append(
                {
                    'name': name,
                    'path': os.path.join(rel_path, name),
                    'is_dir': os.path.isdir(full_path),
                    'size': stat.st_size if not os.path.isdir(full_path) else 0,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                }
            )

        serializer = FileItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        rel_path = request.data.get('path', '')
        upload = request.FILES.get('file')

        if not upload:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        save_dir = os.path.join(settings.MEDIA_ROOT, rel_path)
        os.makedirs(save_dir, exist_ok=True)

        save_path = os.path.join(save_dir, upload.name)
        with open(save_path, 'wb+') as f:
            for chunk in upload.chunks():
                f.write(chunk)

        return Response({'message': f'Uploaded {upload.name}'}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        rel_path = request.query_params.get('path', '')
        abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)

        if not os.path.exists(abs_path):
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        if os.path.isdir(abs_path):
            os.rmdir(abs_path)
        else:
            os.remove(abs_path)

        return Response({'message': f'Deleted {rel_path}'}, status=status.HTTP_200_OK)
