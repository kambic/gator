"""
-------------------------------
Function-Based API Views (FBV)
-------------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sample_api_view(request):

    if request.method == 'GET':
        data = {"message": "This is a GET response"}
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = {"message": "This is a POST response"}
        return Response(data, status=status.HTTP_201_CREATED)

-------------------------------
Class-Based API Views (CBV)
-------------------------------
class SampleAPIView(APIView):
    def get(self, request, *args, **kwargs):
        data = {"message": "This is a GET response from CBV"}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        ...

    def put(self, request, *args, **kwargs):
        ...

    def delete(self, request, *args, **kwargs):
        ...
"""

from datetime import datetime

# views.py
from pathlib import Path

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.filesystem import get_absolute_path, format_item, ROOT_PATH
from .serializers import *


import os
import shutil
from pathlib import Path
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status


class EdgeViewSet(viewsets.ModelViewSet):
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer


@api_view(['GET'])
def directory_list(request):
    dir_path = request.GET.get('path', '')
    try:
        abs_path = get_absolute_path(dir_path)
        if not abs_path.is_dir():
            return JsonResponse({"result": "error", "message": "Not a directory"}, status=400)

        items = []
        for item in sorted(abs_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            if item.name.startswith('.'):  # hide hidden files
                continue
            items.append(format_item(item))

        # Add parent directory if not root
        parent = None
        if str(abs_path.resolve()) != str(ROOT_PATH.resolve()):
            parent_path = abs_path.parent
            parent = format_item(parent_path, name="..")

        return JsonResponse(
            {
                "result": {
                    "items": items,
                    "parent": parent['path'] if parent else None,
                    "dirname": dir_path or "/",
                }
            }
        )
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)}, status=500)


@api_view(['POST'])
def create_directory(request):
    path = request.data.get('path', '').strip('/')
    name = request.data.get('name')

    try:
        new_dir = get_absolute_path(os.path.join(path, name))
        new_dir.mkdir(parents=True, exist_ok=False)
        return JsonResponse({"result": format_item(new_dir)})
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)}, status=400)


@api_view(['POST'])
def rename_item(request):
    path = request.data.get('path')
    new_name = request.data.get('new_name')

    try:
        old_path = get_absolute_path(path)
        new_path = old_path.parent / new_name
        old_path.rename(new_path)
        return JsonResponse({"result": format_item(new_path, new_name)})
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)}, status=400)


@api_view(['POST'])
def delete_items(request):
    items = request.data.get('items', [])
    deleted = []

    for item_path in items:
        try:
            path = get_absolute_path(item_path)
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted.append(item_path)
        except Exception:
            continue  # silently skip failed deletions

    return JsonResponse({"result": deleted})


@api_view(['POST'])
def move_items(request):
    items = request.data.get('items', [])
    to = request.data.get('to', '')

    try:
        dest_dir = get_absolute_path(to)
        if not dest_dir.is_dir():
            return JsonResponse({"result": "error", "message": "Destination not directory"}, status=400)

        moved = []
        for item_path in items:
            src = get_absolute_path(item_path)
            dest = dest_dir / src.name

            # Handle name conflict
            counter = 1
            original = dest
            while dest.exists():
                dest = original.parent / f"{original.stem} ({counter}){original.suffix}"
                counter += 1

            shutil.move(str(src), str(dest))
            moved.append(str(dest.relative_to(ROOT_PATH).as_posix()))

        return JsonResponse({"result": moved})
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)}, status=400)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload(request):
    path = request.data.get('path', '')
    uploaded_file = request.FILES.get('file')

    if not uploaded_file:
        return JsonResponse({"result": "error", "message": "No file uploaded"}, status=400)

    try:
        upload_dir = get_absolute_path(path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        destination = upload_dir / uploaded_file.name

        # Handle overwrite or duplicate names
        if destination.exists():
            counter = 1
            stem = destination.stem
            suffix = destination.suffix
            while destination.exists():
                destination = destination.parent / f"{stem} ({counter}){suffix}"
                counter += 1

        with open(destination, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return JsonResponse({"result": format_item(destination)})
    except Exception as e:
        return JsonResponse({"result": "error", "message": str(e)}, status=500)


@api_view(['GET'])
def download(request):
    file_path = request.GET.get('path')
    if not file_path:
        raise Http404

    try:
        path = get_absolute_path(file_path)
        if not path.is_file():
            raise Http404

        response = FileResponse(open(path, 'rb'), as_attachment=True, filename=path.name)
        return response
    except Exception:
        raise Http404


class FileListView(APIView):
    BASE_DIR = Path('/export/isilj')

    def get(self, request, path=''):
        raw_path = path.strip('/')
        if raw_path:
            full_path = (self.BASE_DIR / raw_path).resolve()
        else:
            full_path = self.BASE_DIR.resolve()

        # === Security check ===
        try:
            if not str(full_path).startswith(str(self.BASE_DIR.resolve())):
                return Response({"error": "Access denied"}, status=403)
        except Exception:
            return Response({"error": "Invalid path"}, status=400)

        if not full_path.exists() or not full_path.is_dir():
            return Response({"error": "Not found"}, status=404)

        # === Build file list ===
        files = []
        try:
            for entry in sorted(full_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
                if entry.name.startswith('.'):
                    continue

                rel_path = entry.relative_to(self.BASE_DIR)
                stat = entry.stat()

                item = {
                    "name": entry.name,
                    "path": str(rel_path).replace("\\", "/"),
                    "is_dir": entry.is_dir(),
                }
                if entry.is_file():
                    item["size"] = stat.st_size
                    item["modified"] = datetime.fromtimestamp(stat.st_mtime)

                files.append(item)
        except PermissionError:
            return Response({"error": "Permission denied"}, status=403)

        # === Generate Breadcrumbs ===
        breadcrumbs = []
        current = ""
        parts = raw_path.split("/") if raw_path else []

        # Root breadcrumb
        breadcrumbs.append(
            {
                "name": "Home",  # or "Files", "Root", etc.
                "path": "",
            }
        )

        # Build each level
        for part in parts:
            if not part:
                continue
            current = f"{current}{part}/" if current else f"{part}/"
            breadcrumbs.append(
                {
                    "name": part,
                    "path": current.rstrip("/"),
                }
            )

        # === Serialize with context for URL building ===
        breadcrumb_serializer = BreadcrumbItemSerializer(breadcrumbs, many=True, context={'request': request})

        file_serializer = FileItemSerializer(files, many=True)

        return Response(
            {
                "current_path": raw_path,  # e.g. "documents/projects"
                "breadcrumbs": breadcrumb_serializer.data,
                "files": file_serializer.data,
            }
        )


class FileListView2(APIView):
    # permission_classes = [IsAuthenticated]  # Uncomment if needed

    BASE_DIR = Path('/safe/base/directory')  # CHANGE THIS to your allowed root!

    def get(self, request, path=''):
        """
        List files in directory
        URL: /api/files/               -> root
             /api/files/documents/
             /api/files/documents/projects/
        """
        # Clean and secure the path
        raw_path = path.strip('/')
        if raw_path:
            requested_path = (self.BASE_DIR / raw_path).resolve()
        else:
            requested_path = self.BASE_DIR.resolve()

        # Prevent directory traversal
        try:
            if not str(requested_path).startswith(str(self.BASE_DIR.resolve())):
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"error": "Invalid path"}, status=status.HTTP_400_BAD_REQUEST)

        if not requested_path.exists():
            return Response({"error": "Path does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if not requested_path.is_dir():
            return Response({"error": "Not a directory"}, status=status.HTTP_400_BAD_REQUEST)

        files = []
        try:
            for entry in sorted(requested_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
                if entry.name.startswith('.'):
                    continue  # Skip hidden files

                rel_path = entry.relative_to(self.BASE_DIR)
                stat = entry.stat()

                file_data = {
                    "name": entry.name,
                    "path": str(rel_path).replace("\\", "/"),  # Always forward slashes
                    "is_dir": entry.is_dir(),
                }

                if entry.is_file():
                    file_data["size"] = stat.st_size
                    file_data["modified"] = datetime.fromtimestamp(stat.st_mtime)

                files.append(file_data)

        except PermissionError:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        serializer = FileItemSerializer(files, many=True)
        return Response(serializer.data)
