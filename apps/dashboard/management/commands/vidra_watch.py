import json

from celery import Celery
from celery.events import EventReceiver
from celery.events.state import State
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django_celery_results.models import TaskResult
from loguru import logger


class TaskMonitor:
    def __init__(self, app):
        self.app = app
        self.state = State()

    def save_task_result(self, task, status, event):
        """Save or update task result in TaskResult model."""
        logger.info(f"TASK {status}: {task.name}[{task.uuid}] {task.info() or {} }")

        TaskResult.objects.update_or_create(
            task_id=task.uuid,
            defaults={
                "task_name": task.name,
                "status": status,
                "worker": getattr(task.worker, "hostname", None),
                "date_done": now() if status in ["SUCCESS", "FAILURE"] else None,
                "traceback": getattr(task, "traceback", None),
                "result": json.dumps(task.info() or {}, default=str),
                "task_args": json.dumps(getattr(task, "args", []) or [], default=str),
                "task_kwargs": json.dumps(
                    getattr(task, "kwargs", {}) or {}, default=str
                ),
            },
        )
        logger.info(f"TASK {status}: {task.name}[{task.uuid}] {task.info() or {} }")

    def handle_task_received(self, event):
        """Handle task-received event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "RECEIVED", event)

    def handle_task_started(self, event):
        """Handle task-started event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "STARTED", event)

    def handle_task_succeeded(self, event):
        """Handle task-succeeded event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "SUCCESS", event)

    def handle_task_failed(self, event):
        """Handle task-failed event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "FAILURE", event)

    def handle_task_retried(self, event):
        """Handle task-retried event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "RETRY", event)

    def handle_task_revoked(self, event):
        """Handle task-revoked event."""
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "REVOKED", event)

    def run(self):
        """Start monitoring Celery events."""
        with self.app.connection() as connection:
            recv = EventReceiver(
                connection,
                handlers={
                    "task-received": self.handle_task_received,
                    "task-started": self.handle_task_started,
                    "task-succeeded": self.handle_task_succeeded,
                    "task-failed": self.handle_task_failed,
                    "task-retried": self.handle_task_retried,
                    "task-revoked": self.handle_task_revoked,
                    "*": self.state.event,  # Capture all other events for state tracking
                },
            )
            logger.info("Starting Celery task monitor...")
            recv.capture(limit=None, timeout=None, wakeup=True)


class Command(BaseCommand):
    help = "Run a Celery event monitor and persist into django_celery_results."

    def add_arguments(self, parser):
        parser.add_argument(
            "env",
            type=str,
            choices=["stag", "prod"],
            help="Flower environment (staging or prod)",
        )

    def handle(self, env, *args, **options):
        if env == "stag":
            from vidra_kit.celery_app.config.staging import Config
        else:
            from vidra_kit.celery_app.config.production import Config

        app = Celery("monitor")

        app.config_from_object(Config)

        monitor = TaskMonitor(app)
        self.stdout.write(
            self.style.SUCCESS(
                "Starting Celery event monitor (SUCCESS/FAILURE/RETRY only)..."
            )
        )
        monitor.run()
