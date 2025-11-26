from django.urls import path

from .views import (
    celery_queue_dashboard,
    celery_queue_table,
    get_child_nodes,
    get_root_nodes,
    reencode_video,
    vod_ingest_list,
    CreateVidraJob,
    CreateVidraJobApi,
    ListVidraJobs,
    FineUploaderView,
    doc_view,
    wunderbaum_tree,
)

app_name = "dashboard"

urlpatterns = [
    path('', vod_ingest_list, name='list'),
    path("upload/", FineUploaderView.as_view(), name="upload"),
    path('admin/dashboard/vidrajob/<int:pk>/reencode/', reencode_video, name='dashboard_vidrajob_reencode'),
    # urls.py
    path('api/files/root/', get_root_nodes, name='root_nodes'),
    path('api/files/children/<path:parent_path>/', get_child_nodes, name='child_nodes'),
    path("vidra/tasks/", ListVidraJobs.as_view(), name="tasks_list"),  # UI list
    path("api/vidra/create/", CreateVidraJobApi.as_view(), name="job_create_api"),
    path("vidra/new-job/", CreateVidraJob.as_view(), name="new_job_ui"),  # UI form
    path('fancytree/', wunderbaum_tree, name='tree'),
    path("docs/", doc_view, name="doc_index"),
    path("docs/<slug:slug>/", doc_view, name="doc_page"),
    # Optional: File info API
    path('celery/dashboard/', celery_queue_dashboard, name='celery_dashboard'),
    path('celery/dashboard/table/', celery_queue_table, name='celery_queue_table'),
    # Tree
]
