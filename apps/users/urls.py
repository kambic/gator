from django.urls import path, re_path

from . import views

# Define the regex pattern for usernames once for cleaner code
# Note: path() uses <str:username> by default, but the original regex is more permissive/specific.
# We'll use re_path where the original regex is needed, but simplify the user-facing URLs.

# Original username regex: [\w@._-]*
USERNAME_REGEX = r"[\w@._-]*"


urlpatterns = [
    # --- UI/Frontend User & Channel Views ---

    # 1. User Profile Views (Using re_path to match the permissive username regex)
    # Consolidated the trailing slash and non-trailing slash patterns into one.
    re_path(r"^user/(?P<username>" + USERNAME_REGEX + r")/?$", views.view_user, name="get_user"),
    path(
        "user/<str:username>/shared_with_me/",
        views.shared_with_me,
        name="shared_with_me",
    ),
    path(
        "user/<str:username>/shared_by_me/",
        views.shared_by_me,
        name="shared_by_me",
    ),
    # Note: The original regex for playlists/about was slightly different ([\w@.]*),
    # but we can assume <str:username> will cover most cases, or use the path component converter.
    # Sticking to path() with converters for cleaner code:
    path(
        "user/<str:username>/playlists/",
        views.view_user_playlists,
        name="get_user_playlists",
    ),
    path(
        "user/<str:username>/about/",
        views.view_user_about,
        name="get_user_about",
    ),
    path("user/<str:username>/edit/", views.edit_user, name="edit_user"),


    # 2. Channel Views
    # Channels often use shorter/simpler tokens, so <str:friendly_token> is appropriate.
    path("channel/<str:friendly_token>/", views.view_channel, name="view_channel"),
    path(
        "channel/<str:friendly_token>/edit/",
        views.edit_channel,
        name="edit_channel",
    ),

    # --- API Views (Using path() where possible) ---

    path('api/v1/whoami/', views.UserWhoami.as_view(), name='user-whoami'),
    path('api/v1/user/token/', views.UserToken.as_view(), name='user-token'),
    path('api/v1/login/', views.LoginView.as_view(), name='user-login'),

    # 3. API User List (Consolidated the trailing slash and non-trailing slash patterns)
    path('api/v1/users/', views.UserList.as_view(), name="api_users"),

    # 4. API User Detail (Using re_path to preserve the original, specific username regex)
    re_path(
        r"^api/v1/users/(?P<username>" + USERNAME_REGEX + r")/?$",
        views.UserDetail.as_view(),
        name="api_get_user",
    ),
    re_path(
        r"^api/v1/users/(?P<username>" + USERNAME_REGEX + r")/contact/$",
        views.contact_user,
        name="api_contact_user",
    ),
]
