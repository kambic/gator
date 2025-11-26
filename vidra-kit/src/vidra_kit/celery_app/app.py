# celery_app/app.py
from celery import Celery
import os

def make_celery(production=False):

    if production:
        from .config.production import Config
    else:
        from .config.staging import Config

    celery_app = Celery('vidra_kit')
    celery_app.config_from_object(Config)
    celery_app.autodiscover_tasks(['celery_app'])  # or your tasks package
    # import celery_app.signals  # noqa: F401
    return celery_app

app = make_celery()
app_prod = make_celery(production=True)
