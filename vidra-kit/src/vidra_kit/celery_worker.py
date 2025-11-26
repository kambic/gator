from celery import Celery

app = Celery("vidra_kit.ingest")
app.config_from_object("vidra_kit.ingest.celery_config")
app.autodiscover_tasks(["vidra_kit.ingest.tasks"])


if __name__ == "__main__":
    args = ["worker", "--loglevel=INFO"]
    app.worker_main(argv=args)
