from .base import *  # noqa: F403


# ----------------------------------------------------------------------
# Email – console backend (see mails in terminal)
# ----------------------------------------------------------------------
# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "relay.ts.telekom.si"
EMAIL_PORT = 25


# ----------------------------------------------------------------------
# Vite dev server (hot-reload)
# ----------------------------------------------------------------------
DJANGO_VITE["default"]["dev_mode"] = False
