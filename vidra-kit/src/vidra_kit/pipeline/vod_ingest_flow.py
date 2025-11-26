from celery import chain
from vidra_kit.ingest.tasks import ingest, metadata, package, publish, upload


def run_vod_ingest_workflow(source_url):
    return chain(
        ingest.ingest_file.s(source_url),
        metadata.extract_metadata.s(),
        package.create_adaptive_package.s(),
        upload.upload_to_streaming_host.s(),
        publish.publish_to_cms.s(),
    )()
