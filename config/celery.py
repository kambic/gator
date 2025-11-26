import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

from celery import Celery
from kombu import Queue

app = Celery('video_encoder')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True
# app.conf.broker_url = 'redis://localhost:6379/0'

# Broker URL (amqp:// for RabbitMQ; add credentials/vhost for prod)
# app.conf.broker_url = 'amqp://user:pass@rabbitmq-host:5672/video_vhost'
app.conf.broker_transport_options = {'confirm_publish': True}  # Required for quorum queues
app.conf.broker_heartbeat = 300  # Match RabbitMQ heartbeat
app.conf.broker_connection_timeout = 10  # Longer for slow starts

# Queue setup (declare durable, quorum queue for video tasks)
app.conf.task_queues = [
    Queue('video', queue_arguments={'x-queue-type': 'classic', 'x-message-ttl': 3600000}),
]
app.conf.task_default_queue = 'video'
app.conf.task_default_delivery_mode = 2  # Persistent (durable messages)

# Acknowledgment and retry (critical for long tasks)
app.conf.task_acks_late = True  # Ack after completion; re-queues on crash
app.conf.task_reject_on_worker_lost = True  # Re-queue unfinished tasks on worker death
app.conf.task_acks_on_failure_or_timeout = True  # Ack even on errors/timeouts

# Prefetch and concurrency (low for memory-heavy encoding)
app.conf.worker_prefetch_multiplier = 1  # One task per process; prevents hoarding
app.conf.worker_concurrency = 1  # Or match CPU cores (e.g., 4 for multi-core encoders); use --concurrency CLI override

# Memory and task limits (restart processes to avoid leaks from video libs like FFmpeg)
app.conf.worker_max_tasks_per_child = 10  # Restart after 10 tasks; combats high-water marks
app.conf.worker_max_memory_per_child = 800000  # 800MB limit (in KB); restart if exceeded
app.conf.worker_cancel_long_running_tasks_on_connection_loss = True  # Kill unfinished on disconnect

# Time limits (soft for cleanup, hard for kill; tune per video length)
app.conf.task_soft_time_limit = 3600  # 1 hour warning (e.g., for cleanup hooks)
app.conf.task_time_limit = 7200  # 2 hours hard kill

# Monitoring and tracking
app.conf.task_track_started = True  # Report 'started' state for progress bars
app.conf.task_send_sent_event = True  # Events for tools like Flower
app.conf.worker_send_task_events = True  # Enable Flower monitoring

# Optional: Disable non-essential features to reduce RabbitMQ load
app.conf.worker_disable_rate_limits = True  # If not using rate limits

if False:
    from kombu import Queue

    # https://docs.celeryq.dev/en/latest/userguide/routing.html#id2

    default_exchange = Exchange('default', type='direct')
    media_exchange = Exchange('media', type='direct')

    app.conf.task_queues = (
        Queue('default', default_exchange, routing_key='default'),
        Queue('videos', media_exchange, routing_key='media.video'),
        Queue('images', media_exchange, routing_key='media.image')
    )
    app.conf.task_default_queue = 'default'
    app.conf.task_default_exchange = 'default'
    app.conf.task_default_routing_key = 'default'
