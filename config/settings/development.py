# cms/settings/development.py
# Import everything from base FIRST
from .base import *  # noqa: F403

# ----------------------------------------------------------------------
# Email – console backend (see mails in terminal)
# ----------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ----------------------------------------------------------------------
# Debug Toolbar
# ----------------------------------------------------------------------
INSTALLED_APPS += [
    "debug_toolbar",
    "corsheaders",
    'django_extensions',
    'silk',
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'silk.middleware.SilkyMiddleware',
] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "::1"]
CORS_ALLOW_ALL_ORIGINS = True
# ----------------------------------------------------------------------
# Vite dev server (hot-reload)
# ----------------------------------------------------------------------
DJANGO_VITE["default"]["dev_mode"] = True
# HUEY
