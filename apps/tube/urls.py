from django.urls import path
from . import views


app_name = 'tube'

urlpatterns = [
    path('', views.tube, name='home'),
]
