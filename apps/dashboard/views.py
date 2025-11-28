import datetime
import glob
import structlog as logging
import os
import shutil
from pathlib import Path

import markdown
from celery import Celery
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from vidra_kit.backends.api import fetch_rabbitmq_queues, RabbitMQMonitor
from ..dashboard.models import FileEntry
from ..dashboard.serializers import JobSerializer
from ..files.helpers import rm_file
from ..files.methods import user_allowed_to_upload
from ..files.models import Media
from .fineuploader import ChunkedFineUploader
from .forms import FineUploaderUploadForm, FineUploaderUploadSuccessForm
from ..utils.mixins import PageTitleMixin

logger = logging.getLogger(__name__)

"""
templates/
├── blog/
│   └── post/
│       ├── list.html         # Read (list view)
│       ├── detail.html       # Read (detail view)
│       ├── create.html       # Create
│       ├── update.html       # Update
│       └── delete.html       # Delete

"""

DOCS_DIR = Path(settings.BASE_DIR) / "docs"

# Path to the directory where ZIP files are located
VOD_INGEST_PATH = '/export/isilj/fenix2'


# --- View to Display Files ---
# Full page view (loads Alpine & HTMX)
def celery_queue_dashboard(request):
    return render(request, 'celery_dashboard.html')


# Partial view (for HTMX refresh)
def celery_queue_table(request):

    monitor = RabbitMQMonitor(
        host="bpl-vidra-03.ts.telekom.si",
        port=15672,
        username="guest",
        password="guest",
        vhost="/",  # or your custom vhost
    )

    celery_queue = monitor.get_all_queues()

    return render(request, 'partials/_queue_table.html', {'queues': celery_queue})


def vod_ingest_list(request):
    """
    Displays a list of all ZIP files found in the VOD_INGEST_PATH.
    """
    # Use glob to find all zip files (recursive=True is optional)
    zip_files = glob.glob(os.path.join(VOD_INGEST_PATH, '**', '*.tar'), recursive=True)

    file_list = []
    for full_path in zip_files:
        try:
            file_list.append(
                {
                    'name': os.path.basename(full_path),
                    # The full path is critical for the POST action
                    'path': full_path,
                    'size': os.path.getsize(full_path),
                    'modified': os.path.getmtime(full_path),
                }
            )
        except OSError:
            # Handle case where file might be deleted between listing and checking stats
            continue

    context = {
        'title': "VOD Ingest Control Panel",
        'file_list': file_list,
        'scan_path': VOD_INGEST_PATH,
    }

    # Use a custom template path, e.g., 'your_app/vod_ingest_list.html'
    return render(request, 'vod_ingest_list.html', context)


def doc_view(request, slug="index"):
    def get_doc_list():
        """Recursively list all Markdown files under /docs."""
        docs = []
        for path in DOCS_DIR.rglob("*.md"):
            rel_path = path.relative_to(DOCS_DIR)
            slug = str(rel_path.with_suffix("")).replace("/", "-")
            docs.append(
                {
                    "name": rel_path.stem.replace("-", " ").title(),
                    "slug": slug,
                }
            )
        return sorted(docs, key=lambda x: x["name"].lower())

    # Map slug back to file path
    md_rel_path = slug.replace("-", "/") + ".md"
    md_path = DOCS_DIR / md_rel_path

    if not md_path.exists():
        return render(request, "404.html", status=404)

    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html = markdown.markdown(
        md_content,
        extensions=["fenced_code", "tables", "codehilite", "toc"],
    )

    docs_list = get_doc_list()

    return render(
        request,
        "doc_page.html",
        {
            "content": html,
            "slug": slug,
            "docs_list": docs_list,
        },
    )


# Named tuple for directory entries


def wunderbaum_tree(request):
    node = request.GET.get("node", "#")  # '#' is root node from FancyTree

    folder_path = Path(settings.TREE_ROOT_FOLDER) if node == "#" else Path(node)

    try:
        folder_path = folder_path.resolve()
        root_path = Path(settings.TREE_ROOT_FOLDER).resolve()

        # Security check — ensure requested path is within TREE_ROOT_FOLDER
        if not folder_path.is_dir() or (root_path not in folder_path.parents and folder_path != root_path):
            return JsonResponse({"error": "Invalid folder path"}, status=400)

        entries = []
        for entry in folder_path.iterdir():
            if entry.name.startswith("."):
                continue  # skip hidden files/folders

            stat = entry.stat()

            # Convert ctime to ISO 8601 string (UTC)
            created_time = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()

            entries.append(
                {
                    "title": entry.name,
                    "key": str(entry.resolve()),
                    "folder": entry.is_dir(),
                    "lazy": entry.is_dir(),
                    "created": created_time,
                    "size": stat.st_size if entry.is_file() else None,
                }
            )

        return JsonResponse(entries, safe=False)

    except Exception as e:
        logger.exception("Error generating tree")
        return JsonResponse({"error": str(e)}, status=500)


class CreateVidraJob(PageTitleMixin, TemplateView):
    template_name = "dashboard/vidra/create.html"
    page_title = "Create Vidra Job"


class CreateVidraJobApi(APIView):
    def post(self, request, format=None):
        serializer = JobSerializer(data=request.data, many=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            tasks = self.enqueue(validated_data)
            logger.info("Created tasks: %s" % tasks)
            return Response(tasks, status=status.HTTP_201_CREATED)
        logger.warning(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def enqueue(self, payloads):
        rabbit = settings.VYDRA["stag"]["broker"]["dsn"]
        queue = "videoencoding"

        tasks = []
        with Celery(broker=rabbit) as cel:
            for payload in payloads:
                task = self._get_task_name(payload)
                logger.debug("[NEW][JOB][%s]: %s" % (task, payload))
                oTask = cel.send_task(task, kwargs=payload, queue=queue)
                tasks.append({"id": oTask.id})

        return tasks

    def _get_task_name(self, payload: dict):
        if self._has_vtt_subtitles(payload):
            return "vydra.tasks.encoding.encode_content_v2"
        return "vydra.tasks.encoding.encode_content"

    def _has_vtt_subtitles(self, payload):
        try:
            return "subtitles" in payload and payload["subtitles"]["info"].endswith("vtt")
        except:
            logger.exception("Error subbtitle check vtt in payload %s" % payload)


class ListVidraJobs(PageTitleMixin, TemplateView):
    template_name = "dashboard/vidra/list.html"
    page_title = "Vidra Jobs"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx = {
            "table_id": "dt-table",
            "ajax_url": "dashboard:tasks_list_api",
            "locale": "sl",
            "columns": [
                {
                    "title": "Created",
                    "data": "created",
                    "filter_type": "daterange",
                    "filter_class": "date-filter",
                },
                {"title": "Name", "data": "name"},
                {"title": "UUID", "data": "uuid"},
                {"title": "Hostname", "data": "hostname"},
                {"title": "Runtime", "data": "runtime"},
                {"title": "Env", "data": "env"},
                {"title": "State", "data": "state", "filter_type": "select"},
            ],
            "state_column_index": 6,
            "date_column_index": 0,
            "extra_ajax_params": {"customer": "$('#customerSearchInput').val()"},
        }

        return ctx


BASE_DIR = settings.TREE_ROOT_FOLDER


def get_root_nodes(request):
    def _list_dir(path, is_root=False):
        if not os.path.isdir(path):
            return []
        items = []
        for name in sorted(os.listdir(path)):
            fpath = os.path.join(path, name)
            rel_key = os.path.relpath(fpath, BASE_DIR).replace('\\', '/')
            is_dir = os.path.isdir(fpath)
            items.append(
                {
                    'title': name,
                    'key': rel_key,
                    'folder': is_dir,
                    'lazy': is_dir,
                    'size': os.path.getsize(fpath) if not is_dir else None,
                }
            )
        return items

    return JsonResponse({'children': _list_dir(BASE_DIR, is_root=True)})


def get_child_nodes(request, parent_path):
    full_path = os.path.normpath(os.path.join(BASE_DIR, parent_path))
    if not full_path.startswith(BASE_DIR):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    return JsonResponse({'children': _list_dir(full_path)})


class FineUploaderView(generic.FormView):
    http_method_names = ("post",)
    form_class_upload = FineUploaderUploadForm
    form_class_upload_success = FineUploaderUploadSuccessForm

    @property
    def concurrent(self):
        return settings.CONCURRENT_UPLOADS

    @property
    def chunks_done(self):
        return self.chunks_done_param_name in self.request.GET

    @property
    def chunks_done_param_name(self):
        return settings.CHUNKS_DONE_PARAM_NAME

    def make_response(self, data, **kwargs):
        return JsonResponse(data, **kwargs)

    def get_form(self, form_class=None):
        if self.chunks_done:
            form_class = self.form_class_upload_success
        else:
            form_class = self.form_class_upload
        return form_class(**self.get_form_kwargs())

    def dispatch(self, request, *args, **kwargs):
        if not user_allowed_to_upload(request):
            raise PermissionDenied  # HTTP 403
        return super(FineUploaderView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.upload = ChunkedFineUploader(form.cleaned_data, self.concurrent)
        if self.upload.concurrent and self.chunks_done:
            try:
                self.upload.combine_chunks()
            except FileNotFoundError:
                data = {"success": False, "error": "Error with File Uploading"}
                return self.make_response(data, status=400)
        elif self.upload.total_parts == 1:
            self.upload.save()
        else:
            self.upload.save()
            return self.make_response({"success": True})
        # create media!
        media_file = os.path.join(settings.MEDIA_ROOT, self.upload.real_path)
        with open(media_file, "rb") as f:
            myfile = File(f)
            new = Media.objects.create(media_file=myfile, user=self.request.user)
        rm_file(media_file)
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, self.upload.file_path))
        return self.make_response({"success": True, "media_url": new.get_absolute_url()})

    def form_invalid(self, form):
        data = {"success": False, "error": "%s" % repr(form.errors)}
        return self.make_response(data, status=400)
