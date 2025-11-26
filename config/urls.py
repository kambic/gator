from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, re_path  # Keep re_path for complex regex needs (like Swagger)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from django.conf.urls.static import static


# --- Schema View Setup (No change needed) ---

schema_view = get_schema_view(
    openapi.Info(title="MediaCMS API", default_version='v1', contact=openapi.Contact(url="https://mediacms.io"), x_logo={"url": "../../static/images/logo_dark.svg"}),
    public=True,
    permission_classes=[
        AllowAny,
    ],
)


def favicon(request):
    return HttpResponse(
        ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' + '<text y=".9em" font-size="90">🐊</text>' + "</svg>"),
        content_type="image/svg+xml",
    )


urlpatterns = [
    path('vod/', include('apps.vod.urls')),
    path('tube/', include('apps.tube.urls')),
    path("admin/", admin.site.urls),
    path("favicon/", favicon),
    path("favicon.ico/", favicon),
    path("core/", include("apps.core.urls")),
    # Core Application URLs
    path("files/", include("apps.files.urls")),
    path("dashboard/", include('apps.dashboard.urls')),
    path("tinymce/", include("tinymce.urls")),
    path(r'filer/', include('filer.urls')),
    # User & Authentication URLs
    path("users/", include("apps.users.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    # API Authentication & Swagger Docs
    path("api-auth/", include("rest_framework.urls")),  # 📝 Replaced re_path with path
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/api/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Admin URL
]

# --- Admin Site Customization (No change needed) ---

admin.site.site_header = "VOD Ingest Control"
admin.site.site_title = "VOD Ingest"
admin.site.index_title = "Administration"

# --- Static/Media Files and Debug Toolbar ---

# Static files should be served by a web server in production, but static() is fine for DEBUG
if settings.DEBUG:
    # 📝 Added static file serving for files in MEDIA_ROOT for local development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if 'debug_toolbar' in settings.INSTALLED_APPS:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
