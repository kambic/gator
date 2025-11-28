"""
Maps API endpoints to their respective views.
Example Integration in Project-Level `urls.py`:
    from django.urls import path, include

    urlpatterns = [
        ...
        path('api/v1/your/path/', include('apps.dashboard.api.v1.urls')),  # API URLs
    ]
"""

from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from .views import *
from . import views

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r"edgewares", EdgeViewSet, basename="edgewares")

urlpatterns = [
    path("", include(router.urls)),
    re_path(r'^files/(?P<path>.*)/$', FileListView.as_view(), name='file-list'),
    # Plus root:
    path('files/', FileListView.as_view(), name='file-list-root'),
    path('directory', views.directory_list, name='directory'),
    path('create', views.create_directory, name='create_dir'),
    path('rename', views.rename_item, name='rename'),
    path('delete', views.delete_items, name='delete'),
    path('move', views.move_items, name='move'),
    path('upload', views.upload, name='upload'),
    path('download', views.download, name='download'),
]
