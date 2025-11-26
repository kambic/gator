from vidra_kit.ingest.workflows import vod_ingest_flow
from vidra_kit.ingest.celery_app import app


# start worker
if __name__ == "__main__":
    # app.register_task(vod_ingest_flow)
    args = ["worker", "--loglevel=INFO"]
    # app.conf.broker = "amqp://admin:mypass@rabbit:5672//"
    app.conf.update(broker_url="amqp://admin:mypass@rabbit:5672//")
    # print(app.conf)
    app.worker_main(argv=args)
