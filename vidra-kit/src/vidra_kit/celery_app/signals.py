# celery_app/signals.py
from celery import signals
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# ------------------------------------------------------------------
# Basic hooks – you can keep or expand them
# ------------------------------------------------------------------

@signals.task_prerun.connect
def before_start(task_id=None, task=None, args=None, kwargs=None, **_):
    """Called right before the task starts executing"""
    logger.info(f"TASK STARTED → {task.name} [id:{task_id}] args={args} kwargs={kwargs}")
    # you can also do: print(...)


@signals.task_postrun.connect
def after_finish(task_id=None, task=None, state=None, **_):
    """Called right after the task finishes (success or failure)"""
    logger.info(f"TASK FINISHED → {task.name} [id:{task_id}] state={state}")


@signals.task_success.connect
def on_success(task_id=None, result=None, task=None, **_):
    logger.info(f"TASK SUCCESS → {task.name} [id:{task_id}] result={result!r}")


@signals.task_failure.connect
def on_failure(task_id=None, exception=None, traceback=None, einfo=None, task=None, args=None, kwargs=None, **_):
    """This is the exact equivalent of your on_failure example"""
    logger.error(
        f"TASK FAILED → {task.name} [id:{task_id}]\n"
        f"Exception: {exception!r}\n"
        f"Args: {args}\n"
        f"Kwargs: {kwargs}\n"
        f"Traceback:\n{einfo.traceback}"
    )


# ------------------------------------------------------------------
# Optional but very useful in production
# ------------------------------------------------------------------

@signals.task_retry.connect
def on_retry(task_id=None, reason=None, task=None, **_):
    logger.warning(f"TASK RETRY → {task.name} [id:{task_id}] reason={reason}")

@signals.task_revoked.connect
def on_revoked(task_id=None, terminated=None, signum=None, expired=None, **_):
    logger.warning(f"TASK REVOKED → id:{task_id} terminated={terminated} expired={expired}")

@signals.worker_process_init.connect
def on_worker_start(**_):
    logger.info("Celery worker process initialized (PID: %s)", os.getpid())

@signals.before_task_publish.connect
def before_publish(sender=None, headers=None, body=None, **kwargs):
    logger.info("Task about to be published from client")

@signals.after_task_publish.connect
def after_publish(sender=None, headers=None, body=None, **kwargs):
    logger.info("Task published from client")
