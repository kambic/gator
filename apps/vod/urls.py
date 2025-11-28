from django.urls import path, include
from . import views
from .views import vod_player, fs


app_name = 'vod'

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.video_list, name='list'),
    path('fs/', fs, name='files'),
    path('explorer/', views.file_tree_view, name='file_tree'),
    path('api/v1/', include('apps.vod.api.v1.urls')),  # API URLs
]
