from vidra_kit.celery_app.app import app, app_prod
# celery_result.py
import os
from celery import Celery
from celery.result import AsyncResult, ResultSet
from typing import Optional, Any, Union, List


class CeleryResultHandler:
    """
    Environment-aware handler for retrieving Celery task results.
    Automatically picks the correct Celery app based on CELERY_ENV.
    """

    _instances = {}  # For singleton per env (optional, but useful)

    def __init__(self, celery_app: Optional[Celery] = None):
        if celery_app:
            self.celery_app = celery_app
        else:
            self.celery_app = self._make_celery_app()

    @classmethod
    def get_instance(cls, celery_app: Optional[Celery] = None) -> 'CeleryResultHandler':
        """Singleton-like access (useful in web requests)"""
        env = os.getenv('CELERY_ENV', 'production')
        key = env
        if key not in cls._instances:
            cls._instances[key] = cls(celery_app)
        return cls._instances[key]

    def _make_celery_app(self) -> Celery:
        env = os.getenv('CELERY_ENV', 'production').lower()

        config_module = {
            'production': 'config.production.Config',
            'staging': 'config.staging.Config',
            'development': 'config.development.Config',
            'testing': 'config.testing.Config',
            'local': 'config.local.Config',
        }.get(env, 'config.staging.Config')  # fallback to staging

        # Dynamic import
        module_path, class_name = config_module.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        config_class = getattr(module, class_name)

        app = Celery('vidra_kit')
        app.config_from_object(config_class())

        # Optional: autodiscover tasks
        app.autodiscover_tasks(['celery_app', 'your_other_tasks_package'])

        return app

    # ------------------------------------------------------------------ #
    # Core methods
    # ------------------------------------------------------------------ #

    def get_result(self,
                   task_id: str,
                   timeout: Optional[float] = 10.0,
                   propagate: bool = True) -> Any:
        """
        Get task result (blocks until ready or timeout).
        """
        result = AsyncResult(task_id, app=self.celery_app)
        return result.get(timeout=timeout, propagate=propagate)

    def get_result_nonblocking(self, task_id: str) -> dict:
        """
        Non-blocking: returns status + result if ready.
        Safe for web views.
        """
        result = AsyncResult(task_id, app=self.celery_app)

        response = {
            "task_id": task_id,
            "status": result.state,
            "ready": result.ready(),
            "successful": result.successful(),
            "failed": result.failed(),
        }

        if result.ready():
            if result.successful():
                response["result"] = result.result
            else:
                # result.result contains the exception
                response["error"] = str(result.result)
                if isinstance(result.result, Exception):
                    response["traceback"] = result.traceback

        return response

    def get_many(self, task_ids: List[str], timeout: float = 10.0) -> List[Any]:
        """
        Get results for multiple tasks efficiently using ResultSet.
        """
        results = ResultSet(AsyncResult(tid, app=self.celery_app) for tid in task_ids)
        return results.get(timeout=timeout)

    def forget(self, task_id: str) -> None:
        """Remove result from backend (free up space)"""
        AsyncResult(task_id, app=self.celery_app).forget()

    def revoke(self, task_id: str, terminate: bool = True) -> None:
        """Revoke/cancel a running task"""
        self.celery_app.control.revoke(task_id, terminate=terminate)


task_id = "44ab7094-4600-496f-ac33-24450ae44aac"
res = AsyncResult(task_id, app=app)  # Important: pass the app if not in the same module
from pprint import pprint
# Check status
print(res.state)   # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE', etc.
print(res.ready()) # True if finished (success or failure)
print(res.successful())  # True only if SUCCESS
print(res.failed())

# Get the actual result (blocks until ready, or raises TimeoutError)
try:
    value = res.get(timeout=10)  # Wait up to 10 seconds
    print(value)  # e.g., 9 for add(4, 5)
except res.TimeoutError:
    print("Task still running or timed out")
except Exception as exc:  # If task raised an exception
    print("Task failed:", exc)


handler = CeleryResultHandler(celery_app=app)
# handler = CeleryResultHandler.get_instance()  # auto-detects env

# Non-blocking (recommended for web)
status = handler.get_result_nonblocking(task_id)
print('status')
pprint(status)

# Blocking (use carefully)
try:
    result = handler.get_result(task_id, timeout=30)
    print("Success:")
    pprint(result)
except TimeoutError:
    print("Task still running...")
except Exception as e:
    print("Task failed:", e)
