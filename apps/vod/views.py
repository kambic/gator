# Create your views here.
# views.py
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Video

BASE_DIR = Path(settings.BASE_DIR)  # Your project root
ALLOWED_ROOT = BASE_DIR  # Change this to restrict (e.g. BASE_DIR / "myapp")


@login_required
def home(request):

    return render(request, 'vod/home.html', {'form': None})


def video_list(request):
    videos = Video.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'vod/list.html', {'videos': videos})


def vod_player(request):
    return render(request, 'vod/player.html')


def fs(request):
    return render(request, 'vod/fs.html')


@require_GET
def file_tree_view(request):
    path_param = request.GET.get("path", "").strip("/")

    # Security: Prevent directory traversal
    try:
        requested_path = (ALLOWED_ROOT / path_param).resolve().relative_to(ALLOWED_ROOT.resolve())
    except (ValueError, OSError):
        return HttpResponseForbidden("Access denied.")

    full_path = ALLOWED_ROOT / requested_path

    if not full_path.exists():
        return HttpResponse("Not found", status=404)

    items = []
    try:
        # List directory contents
        for entry in sorted(full_path.iterdir(), key=lambda e: (e.is_file(), e.name.lower())):
            if entry.name.startswith('.'):  # Skip hidden files
                continue
            rel_path = str(requested_path / entry.name) if str(requested_path) != "." else entry.name
            items.append(
                {
                    "name": entry.name,
                    "type": "folder" if entry.is_dir() else "file",
                    "path": rel_path.replace("\\", "/"),  # Normalize for Windows
                }
            )
    except PermissionError:
        return HttpResponseForbidden("Permission denied.")

    return render(
        request,
        "vod/partials/_file_tree_children.html",
        {
            "items": items,
            "current_path": str(requested_path).replace("\\", "/"),
        },
    )
