from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path, re_path

from . import management_views, views
from .feeds import IndexRSSFeed, SearchRSSFeed


urlpatterns = [
    # --- I18N, Root, and Utility URLs ---
    path("i18n/", include("django.conf.urls.i18n")),
    # Using path() and removing the unnecessary caret (^) in the regex
    path("", views.index, name="index"),  # 📝 Renamed root view for clarity
    path("about/", views.about, name="about"),  # 📝 Added trailing slash
    path("setlanguage/", views.setlanguage, name="setlanguage"),  # 📝 Added trailing slash
    path("contact/", views.contact, name="contact"),  # 📝 Added trailing slash
    path("tos/", views.tos, name="terms_of_service"),  # 📝 Added trailing slash
    # --- Media Management URLs (Standard Views) ---
    path("add_subtitle/", views.add_subtitle, name="add_subtitle"),
    path("edit_subtitle/", views.edit_subtitle, name="edit_subtitle"),
    path("publish/", views.publish_media, name="publish_media"),  # 📝 Cleaned /publish
    path("edit_chapters/", views.edit_chapters, name="edit_chapters"),
    path("edit_video/", views.edit_video, name="edit_video"),
    path("edit/", views.edit_media, name="edit_media"),
    path("embed/", views.embed_media, name="get_embed"),
    path("upload/", views.upload_media, name="upload_media"),
    path("scpublisher/", views.upload_media, name="scpublisher_upload"),  # 📝 Rename for uniqueness
    path("record_screen/", views.record_screen, name="record_screen"),
    # --- Content Discovery URLs (Standard Views) ---
    path("categories/", views.categories, name="categories"),
    path("featured/", views.featured_media, name="featured_media"),  # 📝 Added name
    path("history/", views.history, name="history"),
    path("liked/", views.liked_media, name="liked_media"),
    path("latest/", views.latest_media, name="latest_media"),  # 📝 Added name
    path("members/", views.members, name="members"),
    path("popular/", views.recommended_media, name="popular_media"),  # 📝 Added name
    path("recommended/", views.recommended_media, name="recommended_media"),  # 📝 Added name
    path("search/", views.search, name="search"),
    path("tags/", views.tags, name="tags"),
    # --- Content Detail URLs (Using path converters) ---
    path("view/", views.view_media, name="get_media"),
    # Use path("media/<str:friendly_token>/") for better structure if possible
    path(
        "playlist/<str:friendly_token>/",
        views.view_playlist,
        name="get_playlist",
    ),
    # 📝 Removed duplicate playlist URL (playlists/<token> vs playlist/<token>)
    # --- Feed and External App URLs ---
    path("rss/", IndexRSSFeed(), name="index_rss_feed"),
    re_path("^rss/search$", SearchRSSFeed(), name="search_rss_feed"),  # Keep re_path for non-standard path matching
    # --- API VIEWS (Using path() and proper prefixes) ---
    # Media List & Bulk Actions
    path("api/v1/media/", views.MediaList.as_view(), name="api_media_list"),
    path("api/v1/media/user/bulk_actions/", views.MediaBulkUserActions.as_view(), name="api_media_bulk_actions"),
    # Media Detail & Actions
    path(
        "api/v1/media/<str:friendly_token>/",
        views.MediaDetail.as_view(),
        name="api_get_media",
    ),
    path(
        "api/v1/media/<str:friendly_token>/actions/",
        views.MediaActions.as_view(),
        name="api_media_actions",
    ),
    path(
        "api/v1/media/<str:friendly_token>/chapters/",
        views.video_chapters,
        name="api_video_chapters",
    ),
    path(
        "api/v1/media/<str:friendly_token>/trim_video/",
        views.trim_video,
        name="api_trim_video",
    ),
    path(
        "api/v1/media/encoding/<str:encoding_id>/",
        views.EncodingDetail.as_view(),
        name="api_get_encoding",
    ),
    # Discovery & Action APIs
    path("api/v1/search/", views.MediaSearch.as_view(), name="api_search"),
    path("api/v1/categories/", views.CategoryList.as_view(), name="api_category_list"),
    path("api/v1/tags/", views.TagList.as_view(), name="api_tag_list"),
    path("api/v1/user/action/<str:action>/", views.UserActions.as_view(), name="api_user_actions"),
    # Comment APIs
    path("api/v1/comments/", views.CommentList.as_view(), name="api_comment_list"),
    path(
        "api/v1/media/<str:friendly_token>/comments/",
        views.CommentDetail.as_view(),  # Handle POST/GET for all comments on media
        name="api_media_comments",
    ),
    path(
        "api/v1/media/<str:friendly_token>/comments/<str:uid>/",
        views.CommentDetail.as_view(),  # Handle GET/PUT/DELETE for specific comment
        name="api_comment_detail",
    ),
    # Playlist APIs
    path("api/v1/playlists/", views.PlaylistList.as_view(), name="api_playlist_list"),
    path(
        "api/v1/playlists/<str:friendly_token>/",
        views.PlaylistDetail.as_view(),
        name="api_get_playlist_detail",
    ),
    # --- ADMIN/MANAGEMENT APIs ---
    path("api/v1/encode_profiles/", views.EncodeProfileList.as_view(), name="api_encode_profiles"),
    path("api/v1/manage_media/", management_views.MediaList.as_view(), name="api_manage_media"),
    path("api/v1/manage_comments/", management_views.CommentList.as_view(), name="api_manage_comments"),
    path("api/v1/manage_users/", management_views.UserList.as_view(), name="api_manage_users"),
    # Task APIs (Consolidated)
    path("api/v1/tasks/", views.TasksList.as_view(), name="api_tasks_list"),
    path(
        "api/v1/tasks/<str:friendly_token>/",
        views.TaskDetail.as_view(),
        name="api_task_detail",
    ),
    # Management HTML Views
    path("manage/comments/", views.manage_comments, name="manage_comments"),
    path("manage/media/", views.manage_media, name="manage_media"),
    path("manage/users/", views.manage_users, name="manage_users"),
    # --- Final Catch-all URL ---
    # This must remain a re_path as it uses a regex ([\w.-]*) and must be the last entry.
    re_path(r"^(?P<slug>[\w.-]*)/$", views.get_page, name="get_page"),
]

# --- Appending Configuration-based URLs ---

# Static files handling is moved to the end of the core URL list for clean separation
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.USERS_NEEDS_TO_BE_APPROVED:
    urlpatterns.append(path("approval_required/", views.approval_required, name="approval_required"))

if hasattr(settings, "USE_SAML") and settings.USE_SAML:
    urlpatterns.append(path("saml/metadata/", views.saml_metadata, name="saml-metadata"))

# if hasattr(settings, "USE_IDENTITY_PROVIDERS") and settings.USE_IDENTITY_PROVIDERS:
#     # Use custom view for /accounts/login when identity providers are active
#     urlpatterns.append(path('accounts/login/', views.custom_login_view, name='login'))
#     # Use allauth's view for the system path
#     urlpatterns.append(path('accounts/login_system/', LoginView.as_view(), name='login_system'))
# else:
#     # Otherwise, use allauth's view for the main login path
#     urlpatterns.append(path('accounts/login/', LoginView.as_view(), name='login'))

if hasattr(settings, "GENERATE_SITEMAP") and settings.GENERATE_SITEMAP:
    urlpatterns.append(path("sitemap.xml", views.sitemap, name="sitemap"))
