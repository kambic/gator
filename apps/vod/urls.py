from django.urls import path
from . import views
from .views import vod_player, fs


app_name = 'vod'

urlpatterns = [
    path('', views.upload_package, name='home'),
    path('list/', views.video_list, name='list'),
    path('fs/', fs, name='files'),
    path('explorer/', views.file_tree_view, name='file_tree'),
]
