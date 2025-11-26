wsgi_app = 'config.wsgi:application'
workers = 4
threads = 2
# worker_class = "gthread"
bind = "0.0.0.0:7777"
timeout = 60
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 50
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"

env = "DJANGO_SETTINGS_MODULE=config.settings.production"
