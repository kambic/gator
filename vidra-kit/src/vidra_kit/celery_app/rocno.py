from celery import Task, Celery


class Staging:
    broker_url = "amqp://vydra:vydra@bpl-vidra-02.ts.telekom.si:5672/celery"
    result_backend = "redis://bpl-vidra-02.ts.telekom.si:6379/5"

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

class Production(Staging):
    broker_url = (
        "amqp://celery:TRaHS84zhkn7cfzE@bpl-vidra-03.ts.telekom.si:5672/vydra_prod"
    )
    result_backend = (
        "db+postgresql://celery:celery@bpl-vidra-03.ts.telekom.si:5432/celery"
    )



app = Celery('vidra_kit')

app.config_from_object(Staging)


class BaseVidraTask(Task):
    """Base class for Vidra Celery tasks."""
    abstract = True
    soft_time_limit = 60 * 60 * 24  # 24 H
    time_limit = 60 * 60 * 24  # 24 H
    autoretry_for = (ConnectionError,)
    max_retries = 3
    retry_backoff = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

    def before_start(self, task_id, args, kwargs):
        print('{0!r} started'.format(task_id))


@app.task( name='vydra.tasks.encoding.encode_content', queue='videoencoding', base=BaseVidraTask)
def encode_content(name, content_id, video, profiles, audio=None, subtitles=None, log=None, seconds=None,
                   field_type='detect', normalize='loudnorm_truepeak', drm_required=True, **kwargs):
    pass


task = encode_content.delay(name='',
                            content_id=None,
                            video={'info': 'isilon-lj-local:temporary/podcasts/185_MatejPecovnik-OnkoMan_ARD_HDF_01a11/185_MatejPecovnik-OnkoMan_ARD_HDF_01a11.mxf',
                                   'type': 'local'},
                            profiles=['adaptive_hd'],
                            adaptive_dest='edgeware', ott_realm='dkino', drm_required=False)

print(task.id)
