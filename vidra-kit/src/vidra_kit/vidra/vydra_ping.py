import shutil
from pathlib import Path

from celery import Celery, group

from vidra_kit import logger
from vidra_kit.vidra.providers import PROVIDERS
from vidra_kit.storage.islon import CopyWithProgress
from celery import Task

class VidraMixin:
    """Mixin for Vidra-specific task functionality."""
    base_dir = Path('/export/isilj/fenix2')

    def __init__(self, provider_username=None):
        self.provider_username = provider_username
        if not provider_username or provider_username not in PROVIDERS:
            raise ValueError(f"Invalid or missing provider: {provider_username}")
        self.provider = PROVIDERS[provider_username]
        self.name = self.provider['tasks']
        self.queue = self.provider['queue']

    @property
    def provider_home(self):
        """Get the provider's home directory path."""
        return self.base_dir / self.provider_username

    def build_payload(self, file: Path) -> dict:
        """Build FTP payload for the given file."""
        if not file.exists():
            raise FileNotFoundError(f"File not found: {file}")
        return {
            "type": "ftp",
            "host": "bpl-phoenix3.ts.telekom.si",
            "port": 2121,
            "passive": True,
            "folder": "/queue/",
            "filesize": file.stat().st_size,
            "filename": file.name,
            "username": self.provider["provider_fs"]["username"],
            "password": self.provider["provider_fs"]["password"],
        }

    def setup_payload(self, file: Path) -> dict:
        """Prepare file and build payload for processing."""
        dest = self.provider_home / file.name
        logger.info(f"Moving {file.name} to {dest}")
        try:
            new = shutil.copy(file, dest)
            logger.info(f"Moving done to {new}")
            return self.build_payload(dest)
        except (shutil.Error, OSError) as e:
            logger.error(f"Failed to copy file {file} to {dest}: {e}")
            raise


class BaseVidraTask(VidraMixin, Task):
    """Base class for Vidra Celery tasks."""
    abstract = True
    soft_time_limit = 60 * 60 * 24  # 24 H
    time_limit = 60 * 60 * 24  #  24 H
    autoretry_for = (ConnectionError,)
    max_retries = 3
    retry_backoff = True

    def __init__(self, provider_username=None):
        VidraMixin.__init__(self, provider_username=provider_username)
        Task.__init__(self)


class VidraTask(BaseVidraTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))

    def before_start(self, task_id, args, kwargs):
        print('{0!r} started'.format(task_id))


class VydraPing:
    def __init__(self, username, filepath, celery_app=None):

        self.username = username
        self.file = Path(filepath)

        self.celery_app = celery_app

        task = VidraTask(provider_username=self.username)

        self.task = celery_app.register_task(task)

        self.logger = logger

        self.provider = PROVIDERS[self.username]

        self.logger.info("vydraping init done")

        if username in ["blitz"]:
            vpv = TSVODPackageValidatorBlitz(provider="blitz")
            cleaned = vpv.cleanup_filename(self.file.name)

            destination = str(self.file.parent / cleaned)
            logger.info("Reanme file from %s", self.file.name)
            logger.info("Reanme file to   %s", destination)
            shutil.move(self.file, destination)

    def validate_path(self):

        print(self.file.as_uri())

    def move_to_vidra_folder(self):

        destination = Path("/export/isilj/fenix2") / self.username / self.file.name

        self.logger.info(destination)

        if destination.is_file():
            logger.info("destination not avaliable")

        # shutil.copy(self.file, destination)
        copier = CopyWithProgress()
        copier.copy(self.file, destination)

    def enqueue(self, ):

        payload = self.task.build_payload(self.file)
        res = self.task.delay(payload)
        logger.info("New task for %s with id: %s" % (self.username, res.id))

        return res

    def task_url(self):
        host = self.broker["host"]
        return f"http://{host}:8080/task/{self.task.id}"


def cel_app():
    from .brokers import Production as Config
    from .brokers import Staging as Config

    app = Celery()

    app.config_from_object(Config)

    return app


def main():
    celery_app = cel_app()

    # inspect_app(celery_app)

    group_ping(celery_app)


def inspect_app(celery_app: Celery):
    i = celery_app.control.inspect()

    print("Active:", i.active())
    print("Reserved:", i.reserved())
    print("Scheduled:", i.scheduled())


def group_ping(celery_app):
    path = Path('/export/isilj/fenix2/cinestarpremiere')

    # i = celery_app.control.inspect()


    task = VidraTask(provider_username=path.name)
    jobs = []
    for packet in path.iterdir():
        if packet.is_file():
            payload = task.build_payload(packet)
            s = task.s(payload)
            jobs.append(s)
    job = group(*jobs)
    print(f"job: {job}")

    result = job.apply_async()
    print(f"result: {result.id}")


if __name__ == "__main__":
    main()
