import json
import os
import queue
import threading
from collections import defaultdict

from celery import Celery
from celery.events import EventReceiver
from celery.events.state import State
from django.db import close_old_connections
from django.utils.timezone import now
from django_celery_results.models import TaskResult

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
import django

django.setup()


class TaskMonitor:
    def __init__(self, app, batch_size=100, flush_interval=10):
        self.app = app
        self.state = State()
        self.batch_size = batch_size  # Max number of events before flushing
        self.flush_interval = flush_interval  # Seconds between flushes
        self.task_queue = queue.Queue()  # Thread-safe queue for task events
        self.task_states = defaultdict(str)  # Track last known state per task
        self.stop_event = threading.Event()  # Signal for thread shutdown
        self.worker_thread = None

    def save_task_result(self, task, status, event):
        """Queue task result for asynchronous processing."""
        if self.task_states[task.uuid] == status:
            return  # Skip if state hasn't changed
        self.task_states[task.uuid] = status
        self.task_queue.put(
            {
                "task_id": task.uuid,
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
            }
        )
        print(f"TASK {status}: {task.name}[{task.uuid}] {task.info() or {}}")

    def flush_buffer(self, buffer):
        """Write buffered task results to the database."""
        if not buffer:
            return

        # Separate create and update operations
        existing_tasks = set(
            TaskResult.objects.filter(
                task_id__in=[task["task_id"] for task in buffer]
            ).values_list("task_id", flat=True)
        )

        to_create = [task for task in buffer if task["task_id"] not in existing_tasks]
        to_update = [task for task in buffer if task["task_id"] in existing_tasks]

        try:
            # Bulk create new tasks
            if to_create:
                TaskResult.objects.bulk_create(
                    [TaskResult(**task) for task in to_create]
                )
                print(f"Created {len(to_create)} task results")

            # Bulk update existing tasks
            if to_update:
                update_objs = []
                for task_data in to_update:
                    task_obj = TaskResult(task_id=task_data["task_id"])
                    for key, value in task_data.items():
                        setattr(task_obj, key, value)
                    update_objs.append(task_obj)
                TaskResult.objects.bulk_update(
                    update_objs,
                    [
                        "task_name",
                        "status",
                        "worker",
                        "date_done",
                        "traceback",
                        "result",
                        "task_args",
                        "task_kwargs",
                    ],
                )
                print(f"Updated {len(to_update)} task results")

        except Exception as e:
            print(f"Error flushing buffer: {e}")
        finally:
            close_old_connections()  # Ensure database connections are closed

    def worker(self):
        """Simplified worker thread to process queued task events."""
        buffer = []
        while not self.stop_event.is_set():
            try:
                # Wait for an event or timeout after flush_interval
                task_data = self.task_queue.get(timeout=self.flush_interval)
                if task_data is None:  # Sentinel for shutdown
                    break
                buffer.append(task_data)

                # Flush if batch size is reached
                if len(buffer) >= self.batch_size:
                    self.flush_buffer(buffer)
                    buffer = []

            except queue.Empty:
                # Flush if buffer has data after timeout
                if buffer:
                    self.flush_buffer(buffer)
                    buffer = []

        # Flush any remaining events on shutdown
        if buffer:
            self.flush_buffer(buffer)

    def handle_task_received(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "RECEIVED", event)

    def handle_task_started(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "STARTED", event)

    def handle_task_succeeded(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "SUCCESS", event)

    def handle_task_failed(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "FAILURE", event)

    def handle_task_retried(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "RETRY", event)

    def handle_task_revoked(self, event):
        self.state.event(event)
        task = self.state.tasks.get(event["uuid"])
        self.save_task_result(task, "REVOKED", event)

    def run(self):
        """Start monitoring Celery events and worker thread."""
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        try:
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
                        "*": self.state.event,
                    },
                )
                print("Starting Celery task monitor...")
                recv.capture(limit=None, timeout=None, wakeup=True)
        finally:
            # Signal worker to stop and wait for it to finish
            self.stop_event.set()
            self.task_queue.put(None)  # Sentinel to trigger final flush
            self.worker_thread.join()


if __name__ == "__main__":
    app = Celery(broker="amqp://guest@localhost//")
    monitor = TaskMonitor(app, batch_size=100, flush_interval=10)
    monitor.run()
