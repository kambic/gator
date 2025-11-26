# celery_app/config/production.py
from .base import BaseConfig

class Config(BaseConfig):
    broker_url = "amqp://celery:TRaHS84zhkn7cfzE@bpl-vidra-03.ts.telekom.si:5672/vydra_prod"
    result_backend = "db+postgresql://celery:celery@bpl-vidra-03.ts.telekom.si:5432/celery"
