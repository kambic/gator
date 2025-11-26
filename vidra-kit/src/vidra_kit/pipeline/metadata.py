from vidra_kit.ingest.celery_app import app


@app.task
def extract_metadata(source_url):
    """
    @TODO: add documentation
    """
    print(f"extract_metadata msg is: {source_url}")
    return {
        "ingest": {"done": True},
        "metadata": {"done": True},
        "package": {"done": False},
        "upload": {"done": False},
        "publish": {"done": False},
    }
