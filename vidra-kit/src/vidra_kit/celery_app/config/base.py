# celery_app/config/base.py
class BaseConfig:
    timezone = 'Europe/Ljubljana'
    enable_utc = False
    task_track_started = True
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    worker_prefetch_multiplier = 1
    broker_pool_limit = 10
    broker_heartbeat = 10
    broker_connection_timeout = 5
    worker_max_tasks_per_child = 100
    result_expires = 60 * 60 * 24 * 365

    task_routes = {
        'tasks.send_email': {'queue': 'email_queue'},
        'tasks.process_image': {'queue': 'image_queue'},
        'tasks.generate_report': {'queue': 'report_queue'},
    }
