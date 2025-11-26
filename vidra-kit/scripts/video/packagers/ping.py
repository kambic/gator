from celery import Celery
from celery import shared_task


@shared_task(name="vydra.tasks.ingest_package_blitz")
def bliz(*args, **kwargs):
    return x + y


class VidraPing:

    stag_queue = "amqp://vydra:vydra@bpl-vidra-02.ts.telekom.si:5672/celery"
    stag_queue = "redis://bpl-vidra-02.ts.telekom.si:6379/5"

    prod_q = "amqp://celery:TRaHS84zhkn7cfzE@bpl-vidra-03.ts.telekom.si:5672/vydra_prod"
    prod = "db+postgresql://celery:celery@bpl-vidra-03.ts.telekom.si:5432/celery"

    def enqueue(self, payloads):
        rabbit = self.prod_q
        queue = "videoencoding"

        tasks = []
        with Celery(broker=rabbit) as cel:
            for payload in payloads:
                task = self._get_task_name(payload)
                logger.debug("[NEW][JOB][%s]: %s" % (task, payload))
                oTask = cel.send_task(task, kwargs=payload, queue=queue)
                tasks.append({"id": oTask.id})
