import os
import django
from celery import Celery
from celery.result import AsyncResult

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.django_celery_results.models import TaskResult
from vidra_kit.vidra.brokers import Staging, vidra_tasks_factory, get_celery_app

app = get_celery_app('prod')

task_id = '7451c2ac-566d-4942-bbbe-7eeb3c530bfd'

# tasks = TaskResult.objects.filter(task_id=task_id)
# print(tasks)
# res = AsyncResult(task_id, app=app)
# print(res)


result = AsyncResult(task_id, app=app)

print("Task status:", result.status)  # e.g., PENDING, STARTED, SUCCESS, FAILURE
print("Task result:", result.result)  # actual result or exception
print("Is ready?", result.ready())  # True if finished (success or failure)
print("Is successful?", result.successful())  # True if finished successfully

# for flower in flowers:
#     # print(res.state)
#     print(res.get())
#     input("Press enter to continue...")
