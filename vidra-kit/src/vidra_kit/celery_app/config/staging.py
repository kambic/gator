# celery_app/config/staging.py
from .base import BaseConfig

class Config(BaseConfig):
    broker_url = "amqp://vydra:vydra@bpl-vidra-02.ts.telekom.si:5672/celery"
    result_backend = "redis://bpl-vidra-02.ts.telekom.si:6379/5"
