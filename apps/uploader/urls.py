# -*- coding: utf-8 -*-
from django.urls import re_path

import apps.dashboard.views
from . import views

app_name = "uploader"

urlpatterns = [
    re_path(r"^upload/$", apps.dashboard.views.FineUploaderView.as_view(), name="upload"),
]
