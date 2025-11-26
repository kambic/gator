Here's a **production-ready, Django-integrated** version of the `CeleryResultHandler` that works seamlessly with Django ORM models, settings, and management commands — perfect for tracking task status/progress in your database.

### Goal
- Store Celery task metadata (status, result, progress, errors) in Django models
- Retrieve results via ORM **or** Celery backend (fallback)
- Environment-aware (still respects `CELERY_ENV`)
- Works in views, APIs, admin, signals, etc.

### 1. Django Model for Task Tracking

```python
# models.py
from django.db import models
from django.contrib.postgres.fields import JSONField  # or models.JSONField in Django 3.1+
from django.utils import timezone


class CeleryTask(models.Model):
    TASK_STATES = (
        ('PENDING', 'Pending'),
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('REVOKED', 'Revoked'),
        ('RETRY', 'Retry'),
    )

    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)  # task name, e.g. 'app.tasks.process_video'
    args = JSONField(null=True, blank=True)
    kwargs = JSONField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=TASK_STATES, default='PENDING')
    result = JSONField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_done = models.DateTimeField(null=True, blank=True)
    progress = models.FloatField(default=0.0, help_text="0-100%")  # optional progress reporting
    meta = JSONField(default=dict, blank=True)  # extra data (user_id, etc.)

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Celery Task"
        verbose_name_plural = "Celery Tasks"

    def __str__(self):
        return f"{self.name or 'Task'} [{self.task_id}] - {self.status}"
```

Run: `python manage.py makemigrations && python manage.py migrate`

### 2. Enhanced CeleryResultHandler with ORM Integration

```python
# celery_utils/result_handler.py
import os
from celery import Celery
from celery.result import AsyncResult
from django.conf import settings
from django.utils.module_loading import import_string

# Import your model (avoid circular imports)
from your_app.models import CeleryTask  # ← change to your actual app


class DjangoCeleryResultHandler:
    _celery_app = None

    @classmethod
    def get_celery_app(cls) -> Celery:
        if cls._celery_app is None:
            cls._celery_app = cls._make_celery_app()
        return cls._celery_app

    @classmethod
    def _make_celery_app(cls) -> Celery:
        env = os.getenv('CELERY_ENV', 'staging').lower()

        config_map = {
            'production': 'config.production.CeleryConfig',
            'staging': 'config.staging.CeleryConfig',
            'development': 'config.development.CeleryConfig',
            'testing': 'config.testing.CeleryConfig',
            'local': 'config.local.CeleryConfig',
        }

        config_path = config_map.get(env, 'config.staging.CeleryConfig')
        config_class = import_string(config_path)

        app = Celery('vidra_kit')
        app.config_from_object(config_class)
        app.autodiscover_tasks()
        return app

    # ------------------------------------------------------------------ #
    # ORM + Celery Hybrid Methods
    # ------------------------------------------------------------------ #

    @classmethod
    def create_task_record(cls, task_id: str, task_name: str, args=None, kwargs=None, **meta) -> CeleryTask:
        """Call this right after task.delay() or apply_async()"""
        return CeleryTask.objects.create(
            task_id=task_id,
            name=task_name,
            args=args or [],
            kwargs=kwargs or {},
            meta=meta,
        )

    @classmethod
    def get_task(cls, task_id: str) -> CeleryTask:
        """Get ORM record (raises DoesNotExist if not tracked)"""
        return CeleryTask.objects.get(task_id=task_id)

    @classmethod
    def refresh_from_celery(cls, task_id: str, commit=True) -> CeleryTask:
        """
        Sync latest status from Celery result backend → Django ORM
        """
        celery_result = AsyncResult(task_id, app=cls.get_celery_app())

        obj, created = CeleryTask.objects.get_or_create(task_id=task_id)

        obj.status = celery_result.state
        if celery_result.ready():
            if celery_result.successful():
                obj.result = celery_result.result
            else:
                obj.result = None
                if celery_result.result:
                    obj.traceback = str(celery_result.result)
                obj.traceback = celery_result.traceback or obj.traceback
            obj.date_done = timezone.now()

        if celery_result.state == 'STARTED':
            obj.date_started = timezone.now()

        if commit:
            obj.save(update_fields=['status', 'result', 'traceback', 'date_done', 'date_started'])

        return obj

    @classmethod
    def get_result(cls, task_id: str, timeout=10.0, fallback_to_celery=True):
        """
        Try ORM first → fallback to Celery backend
        """
        try:
            task = CeleryTask.objects.get(task_id=task_id)
            if task.status == 'SUCCESS':
                return task.result
            elif task.status in ('FAILURE', 'REVOKED'):
                raise task.result or Exception(f"Task {task.status.lower()}")
            elif task.status in ('PENDING', 'STARTED'):
                if fallback_to_celery:
                    return cls.refresh_from_celery(task_id).result  # may block
        except CeleryTask.DoesNotExist:
            if fallback_to_celery:
                return AsyncResult(task_id, app=cls.get_celery_app()).get(timeout=timeout)

        raise TimeoutError(f"Task {task_id} not ready yet")

    @classmethod
    def get_status(cls, task_id: str) -> dict:
        """Fast status check (great for polling in API)"""
        try:
            task = CeleryTask.objects.only('status', 'progress', 'result').get(task_id=task_id)
            return {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress,
                "ready": task.status in ('SUCCESS', 'FAILURE', 'REVOKED'),
                "result": task.result if task.status == 'SUCCESS' else None,
            }
        except CeleryTask.DoesNotExist:
            # Fallback to Celery
            res = AsyncResult(task_id, app=cls.get_celery_app())
            return {
                "task_id": task_id,
                "status": res.state,
                "progress": 0.0,
                "ready": res.ready(),
                "result": res.result if res.successful() else None,
            }
```

### 3. Example Usage in Views / Tasks

```python
# views.py (e.g., APIView or View)
from rest_framework.views import APIView
from rest_framework.response import Response
from .result_handler import DjangoCeleryResultHandler as handler
from your_app.tasks import process_video

class StartVideoProcessing(APIView):
    def post(self, request):
        video_file = request.FILES['video']
        task = process_video.delay(video_file.id, user_id=request.user.id)

        # Save to ORM immediately
        handler.create_task_record(
            task_id=task.id,
            task_name='your_app.tasks.process_video',
            kwargs={'video_id': video_file.id},
            user_id=request.user.id
        )

        return Response({"task_id": task.id})


### How to configure and use the tools
- Make sure that you have all the required installations (`cli-tool/requirements.txt`)installed. To install it -
    - Create a new virtualenv using any python virtualenv manager.
    - Then activate the virtualenv and enter `pip install -r requirements.txt`.
- Create an .env file in this folder (`mediacms/cli-tool/`)
- Run the cli tool using the command `python cli.py login`. This will authenticate you and store necessary creds for further authentications.
- To check the credentials and necessary setup, run `python cli.py whoami`. This will show your details.
