import os
from pathlib import Path

import environ
from celery.schedules import crontab
from django.utils.translation import gettext_lazy as _

env = environ.Env(DEBUG=(bool, False))
# BASE_DIR = environ.Path(__file__) - 3

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
# =============================================================================
# CORE SETTINGS
# =============================================================================
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
FRONTEND_HOST = env('FRONTEND_HOST')

FRONTEND_URL = FRONTEND_HOST

INTERNAL_IPS = ["127.0.0.1"]

SITE_ID = 1
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# =============================================================================
# APPLICATIONS
# =============================================================================
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # "jazzmin",
    "django.contrib.admin",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "imagekit",
    "mptt",
    "crispy_forms",
    "crispy_bootstrap5",
    "djcelery_email",
    "drf_yasg",
    "tinymce",
    "django_celery_results",
    "import_export",
    "django_htmx",
    "django_vite",
    # "taggit",
    # Local apps
    "apps.files.apps.FilesConfig",
    "apps.users.apps.UsersConfig",
    # "apps.uploader.apps.UploaderConfig",
    "apps.dashboard",
    "apps.core",
    "apps.vod",
    'easy_thumbnails',
    'filer',
]

VUEFINDER_ROOT = '/srv'
# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

USERS_NEEDS_TO_BE_APPROVED = False

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

# =============================================================================
# URLS & PATHS
# =============================================================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "manifest_path": "assets/manifest.json",
        # "manifest_path": "apps/dashboard/static/assets/manifest.json",
    }
}

# Media subdirectories
MEDIA_UPLOAD_DIR = "original/"
MEDIA_ENCODING_DIR = "encoded/"
THUMBNAIL_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}thumbnails/"
SUBTITLES_UPLOAD_DIR = f"{MEDIA_UPLOAD_DIR}subtitles/"
HLS_DIR = MEDIA_ROOT / "hls"

TEMP_DIRECTORY = "/tmp"
MASK_IPS_FOR_ACTIONS = False

# =============================================================================
# TEMPLATES
# =============================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        # "APP_DIRS": True,
        "OPTIONS": {
            'loaders': [
                # App directories first
                'django.template.loaders.app_directories.Loader',
                # Then global templates
                'django.template.loaders.filesystem.Loader',
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
                "apps.files.context_processors.stuff",
            ],
        },
    },
]
# =============================================================================
# DATABASE
# =============================================================================

DATABASES = {
    'default': env.db(),
}
# =============================================================================
# CACHE & SESSIONS
# =============================================================================
REDIS_LOCATION = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    'default': env.cache(),
}

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = "default"

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Ljubljana"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
    ("sl", _("Slovenian")),
]

# =============================================================================
# AUTH & USER SETTINGS
# =============================================================================
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "/core/shaka/"

# =============================================================================
# SECURITY
# =============================================================================
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "ALLOWALL"  # Consider DENY or SAMEORIGIN in production

# =============================================================================
# EMAILS
# =============================================================================
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

SERVER_EMAIL = env("SERVER_EMAIL", default="root@localhost")
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_SUBJECT_PREFIX = "[Koordinator] "
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

EMAIL_HOST = 'relay.ts.telekom.si'
EMAIL_PORT = 25
ADMIN_EMAIL_LIST = ["rok.kambic@telekom.si"]

# =============================================================================
# REST FRAMEWORK
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
}

# =============================================================================
# CELERY
# =============================================================================
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_SOFT_TIME_LIMIT = 2 * 3600
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_RESULT_EXTENDED = True

CELERY_EMAIL_TASK_CONFIG = {"queue": "short_tasks"}

CELERY_BEAT_SCHEDULE = {
    "clear_sessions": {
        "task": "django.core.management.call_command",
        "schedule": crontab(hour=1, minute=1, day_of_week=6),
        "args": ("clearsessions",),
    },
    "get_list_of_popular_media": {
        "task": "get_list_of_popular_media",
        "schedule": crontab(minute=1, hour="*/10"),
    },
    "update_listings_thumbnails": {
        "task": "update_listings_thumbnails",
        "schedule": crontab(minute=2, hour="*/30"),
    },
}

CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

# =============================================================================
# LOGGING
# =============================================================================
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        'colorful': {'format': '\033[1;34m%(levelname)s \033[1;35m%(name)s:%(module)s \033[0m%(funcName)s %(message)s'},
    },
    "handlers": {
        'mail_admins': {'level': 'ERROR', 'class': 'django.utils.log.AdminEmailHandler'},
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "debug.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'colorful'},
    },
    "loggers": {
        # This logger captures Django's core functions (requests, errors, etc.)
        "django": {
            "handlers": ["console", "file"],  # Direct all Django logs to both console and file
            "level": "INFO",
            "propagate": False,  # Stop logs from bubbling up to the root logger
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        # This logger is crucial for seeing database queries
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  # Set to DEBUG to see all SQL queries
            "propagate": False,
        },
        # Add your own app logger for custom messages
        "apps.dashboard": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# =============================================================================
# PORTAL & UI SETTINGS
# =============================================================================
PORTAL_NAME = "MediaCMS"
PORTAL_DESCRIPTION = "Vidra Dashboard"
DEFAULT_THEME = "light"

CAN_ADD_MEDIA = "email_verified"
CAN_COMMENT = "email_verified"
PORTAL_WORKFLOW = "public"

LOGIN_ALLOWED = True
UPLOAD_MEDIA_ALLOWED = True
CAN_LIKE_MEDIA = CAN_DISLIKE_MEDIA = CAN_REPORT_MEDIA = CAN_SHARE_MEDIA = True

REPORTED_TIMES_THRESHOLD = 10
ALLOW_ANONYMOUS_ACTIONS = ["report", "like", "dislike", "watch"]
TIME_TO_ACTION_ANONYMOUS = 10 * 60

MEDIA_IS_REVIEWED = True
SHOW_ORIGINAL_MEDIA = True
MAX_MEDIA_PER_PLAYLIST = 70
UPLOAD_MAX_SIZE = 800 * 1024 * 1000 * 5 * 10
MAX_CHARS_FOR_COMMENT = 10000
TIMESTAMP_IN_TIMEBAR = False
ALLOW_MENTION_IN_COMMENTS = True
RELATED_MEDIA_STRATEGY = "content"

# Logos
PORTAL_LOGO_DARK_SVG = "/static/images/logo_dark.svg"
PORTAL_LOGO_DARK_PNG = "/static/images/logo_dark.png"
PORTAL_LOGO_LIGHT_SVG = "/static/images/logo_light.svg"
PORTAL_LOGO_LIGHT_PNG = "/static/images/logo_dark.png"

EXTRA_CSS_PATHS = []

# =============================================================================
# MEDIA PROCESSING
# =============================================================================
FFMPEG_COMMAND = "ffmpeg"
FFPROBE_COMMAND = "ffprobe"
MP4HLS_COMMAND = "/usr/local/Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp42hls"
PYSUBS_COMMAND = "pysubs2"

DO_NOT_TRANSCODE_VIDEO = False
MINIMUM_RESOLUTIONS_TO_ENCODE = [360, 480]
CHUNKIZE_VIDEO_DURATION = 60 * 5
VIDEO_CHUNKS_DURATION = 60 * 4
RUNNING_STATE_STALE = 60 * 60 * 2
FRIENDLY_TOKEN_LEN = 9

UPLOAD_DIR = "uploads/"
CHUNKS_DIR = "chunks/"
UPLOAD_MAX_FILES_NUMBER = 100
CONCURRENT_UPLOADS = True
FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# =============================================================================
# THIRD-PARTY CONFIG
# =============================================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DJANGO_ADMIN_URL = "admin/"

# =============================================================================
# JAZZMIN ADMIN
# =============================================================================
JAZZMIN_SETTINGS = {
    "site_title": "Vidra Library",
    "site_header": "Vidra Library",
    "site_brand": "Vidra Library",
    # "site_logo": "img/logo.png",
    # "login_logo": "img/login-logo.png",
    # "site_icon": "img/favicon.ico",
    # Welcome & copyright
    "welcome_sign": "Welcome to the Vidra library",
    "copyright": "Telekom",
    # Layout
    "navigation_expanded": True,
    "hide_apps": [],  # e.g., ['auth']
    "hide_models": [],
    # UI Builder (toggle in admin)
    "show_ui_builder": True,
    "search_model": ["dashboard.Provider", "dashboard.Edgeware"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Manuals", "url": "/dashboard/docs/index/", "new_window": True},
    ],
    # Colors (AdminLTE theme)
    "theme": "default",  # or "dark", "cyborg", "flatly", etc.
    "dark_mode_theme": "dark",
    # Icons
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "dashboard.vidrajob": "fas fa-cog",
        "dashboard.provider": "fas fa-box-open",
        "dashboard.edgeware": "fas fa-video",
        "dashboard.expirededgeware": "fas fa-archive",
        "dashboard.sftpgoevent": "fas fa-file-arrow-up",
        "media.media": "fas fa-film",
        "files.transcriptionrequest": "fas fa-closed-captioning",
        "files.subtitle": "fas fa-closed-captioning",
        "files.category": "fas fa-folder-tree",
        "files.comment": "fas fa-comments",
        "files.encodeprofile": "fas fa-sliders-h",
        "files.encoding": "fas fa-spinner",
        "files.language": "fas fa-language",
        "files.media": "fas fa-photo-video",
        "files.page": "fas fa-file-alt",
        "files.tag": "fas fa-tags",
        "files.tinymcemedia": "fas fa-photo-video",
        "files.videotrimrequest": "fas fa-cut",
        "users.user": "fas fa-user",
        "account.emailaddress": "fas fa-envelope",
        "rbac.rbacgroup": "fas fa-users",
        "django_celery_results.groupresult": "fas fa-layer-group",
        "django_celery_results.taskresult": "fas fa-tasks",
        "sites.site": "fas fa-globe",
        "taggit.tag": "fas fa-tag",
    },
    "use_google_fonts_cdn": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "actions_sticky_top": True,
}

# =============================================================================
# TINYMCE
# =============================================================================
TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "resize": "both",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist,autolink,autosave,lists,link,image,charmap,print,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,directionality,"
    "code,help,wordcount,emoticons,file,image,media",
    "toolbar": "undo redo | code preview | blocks | bold italic | alignleft aligncenter "
    "alignright alignjustify ltr rtl | bullist numlist outdent indent | "
    "removeformat | restoredraft help | image media",
    "branding": False,
    "promotion": False,
    "body_class": "page-main-inner custom-page-wrapper",
    "block_formats": "Paragraph=p; Heading 1=h1; Heading 2=h2; Heading 3=h3;",
    "font_size_formats": "16px 18px 24px 32px",
    "images_upload_url": "/tinymce/upload/",
    "images_upload_handler": "tinymce.views.upload_image",
    "automatic_uploads": True,
    "file_picker_types": "image",
    "paste_data_images": True,
    "paste_as_text": False,
}

# =============================================================================
# FEATURE FLAGS
# =============================================================================
LOCAL_INSTALL = True
USE_SAML = False
USE_RBAC = True
USE_IDENTITY_PROVIDERS = False
USE_ROUNDED_CORNERS = True
ALLOW_VIDEO_TRIMMER = True
ALLOW_CUSTOM_MEDIA_URLS = True
ALLOW_ANONYMOUS_USER_LISTING = False
CAN_SEE_MEMBERS_PAGE = "editors"
NUMBER_OF_MEDIA_USER_CAN_UPLOAD = 100
ALLOWED_MEDIA_UPLOAD_TYPES = ["video", "audio", "image", "pdf"]
USE_WHISPER_TRANSCRIBE = False
WHISPER_MODEL = "base"
SIDEBAR_FOOTER_TEXT = "vidra"

USERS_NOTIFICATIONS = {
    "MEDIA_ADDED": True,  # in use
    "MEDIA_ENCODED": False,  # not implemented
    "MEDIA_REPORTED": True,  # in use
}

ADMINS_NOTIFICATIONS = {
    "NEW_USER": True,  # in use
    "MEDIA_ADDED": True,  # in use
    "MEDIA_ENCODED": False,  # not implemented
    "MEDIA_REPORTED": True,  # in use
}

# this is for fineuploader - media uploads
CHUNKS_DONE_PARAM_NAME = "done"


def build_dsn(broker):
    return f"amqp://{broker['username']}:{broker['password']}" f"@{broker['host']}:{broker['port']}/{broker['vhost']}"


VYDRA = {
    "stag": {
        "broker": {
            "host": "bpl-vidra-02.ts.telekom.si",
            "port": 5672,
            "vhost": "celery",
            "username": "vydra",
            "password": "vydra",
        },
        "storage": {"root": "/export/isilj/", "map": "isilon-lj-local:"},
        "result_backend": "redis://bpl-vidra-02.ts.telekom.si:6379/5",
    },
    "prod": {
        "broker": {
            "host": "bpl-vidra-03.ts.telekom.si",
            "port": 5672,
            "vhost": "vydra_prod",
            "username": "celery",
            "password": "TRaHS84zhkn7cfzE",
        },
        "storage": {"root": "/export/isilj/", "map": "isilon-lj-local:"},
        "result_backend": "db+postgresql://celery:celery@bpl-vidra-03.ts.telekom.si:5432/celery",
    },
}
TREE_ROOT_FOLDER = "/export/isilj/fenix2"

# Now add the DSN key for each env by building it dynamically
for _env in VYDRA.values():
    _env["broker"]["dsn"] = build_dsn(_env["broker"])

MAILING_LIST = {
    "from": "bpl-vidra-03@telekom.si",
    "to": [
        "rok.kambic@gmail.com",
        "rok.mehle@telekom.si",
        "tomaz.zelic@telekom.si",
        "katarina.ciber@telekom.si",
        "matej.pengov@telekom.si",
        "peter.ulcnik@telekom.si",
        # "sebastijan.lipnik@gmail.com",
        "basti@slipstream.si",
    ],
}

ATEME = {"username": "vydra", "password": "QWpppL00L!"}

VIDEO_TRANSCODING_CONFIG = {
    "VIDEO_MODEL": "video_transcoding.Video",
}
ADMINS = [
    ("Rok Kambic", "rok.kambic@telekom.si"),
]

PRE_UPLOAD_MEDIA_MESSAGE = ""
POST_UPLOAD_AUTHOR_MESSAGE_UNLISTED_NO_COMMENTARY = ""
ALLOW_RATINGS = False
ALLOW_RATINGS_CONFIRMED_EMAIL_ONLY = True
VIDEO_PLAYER_FEATURED_VIDEO_ON_INDEX_PAGE = False
CANNOT_ADD_MEDIA_MESSAGE = "User cannot add media, or maximum number of media uploads has been reached."
INCLUDE_LISTING_NUMBERS = True
USER_SEARCH_FIELD = "name_username"
