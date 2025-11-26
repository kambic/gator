from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api.views import ProviderViewSet, EdgewareViewSet
from .views import FileAPIView, Components, ShakaPlayer

router = DefaultRouter()
router.register(r'providers', ProviderViewSet, basename='providers')
router.register(r'edge', EdgewareViewSet, basename='edge')
app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('shaka/', ShakaPlayer.as_view(), name='shaka'),
    path('edgewares/', views.EdgewareListView.as_view(), name='edgeware-list'),
    # New HTML views
    path('providers/', views.ProviderListView.as_view(), name='vod-providers-list'),
    path('providers/<int:pk>/', views.ProviderDetailView.as_view(), name='providers-detail'),
    path('files/', views.file_explorer, name='file_explorer'),
    # ✅ File API
    path('api/files/', FileAPIView.as_view(), name='file_api'),
    path('api/', include(router.urls)),
]
