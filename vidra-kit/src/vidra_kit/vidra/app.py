from celery import Celery


from vidra_kit import logger
from .providers import PROVIDERS


class Config:
    # enable_utc = True
    # timezone = 'UTC'
    timezone = 'Europe/Ljubljana'
    # result_backend = "rpc://"
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    task_track_started = True

    result_expires = 60 * 60 * 24 * 365
    worker_max_tasks_per_child = 100
    # task_acks_late = True
    broker_pool_limit = 10  # Limit concurrent connections
    broker_heartbeat = 10
    broker_connection_timeout = 5
    worker_prefetch_multiplier = 1

    task_queues = {
            "high_priority": {"exchange": "high_priority", "routing_key": "high_priority"},
            "default": {"exchange": "default", "routing_key": "default"},
        }



class Staging(Config):
    broker_url = "amqp://vydra:vydra@bpl-vidra-02.ts.telekom.si:5672/celery"
    result_backend = "redis://bpl-vidra-02.ts.telekom.si:6379/5"
    # broker = "amqp://vydra:vydra@bpl-vidra-02.ts.telekom.si:5672/celery"


class Production(Config):
    broker_url = (
        "amqp://celery:TRaHS84zhkn7cfzE@bpl-vidra-03.ts.telekom.si:5672/vydra_prod"
    )
    result_backend = (
        "db+postgresql://celery:celery@bpl-vidra-03.ts.telekom.si:5432/celery"
    )


def get_celery_app(env):
    app = Celery('vidra')
    config = Staging() if env.lower() == 'stag' else Production()
    app.config_from_object(config)
    return app


def vidra_tasks_factory():
    """
    Register tasks from vidra to celery.
    """
    tasks = []

    for provider in PROVIDERS:
        logger.info('Registering provider task: %s' % provider)

        task = VidraTask(provider_username=provider)

        tasks.append(task)

    return tasks
