import ftplib
import json
import logging
from pathlib import Path
from time import sleep
from uuid import uuid4

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class AtemeApi:

    base_url = "http://10.122.22.70/titanfile"
    headers = {"Content-Type": "application/json"}

    def login_ateme(self):
        url = f"{self.base_url}/users/token"

        payload = json.dumps(settings.ATEME)

        response = requests.request(
            "POST", url, headers={"Content-Type": "application/json"}, data=payload
        )

        tokens = response.json()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {tokens['access_token']}",
        }

    def get_job(self, task_id):
        self.login_ateme()

        url = f"{self.base_url}/api/jobs/{task_id}"

        response = requests.get(
            url,
            headers=self.headers,
        )
        response.raise_for_status()

        data = response.json()
        logger.debug("Ateme job: %s", data)

        return data.json()


class PublishEW:
    FTP_HOST = "isilj.ts.telekom.si"
    FTP_USER = "ftpott"
    FTP_PASS = "ft17pott"
    FTP_REMOTE_DIR = "vod/ateme/"
    LOCAL_DIR = "/export/isilj/ateme-tests/output/api/Candice_Cheese_Macejkovic/"

    EW_KEY = "wgXfC6EHEAjQt8wvzErgRE"
    EW_API = "http://ew-api.tv.telekom.si:8090/api/2/content"

    EW_SECRET = "kdmgj7390s"

    def __init__(self, src_dir, content_id=None) -> None:
        self.src_dir = Path(src_dir)
        self.title = self.src_dir.name
        self.ftp_folder = self.FTP_REMOTE_DIR + self.src_dir.name

        self.content_id = content_id if content_id else str(uuid4())
        self.ew = Edgeware.objects.create(title=self.title, ftp_dir=self.ftp_folder)

    def edgeware_check(self):
        headers = {"x-account-api-key": self.EW_KEY}
        url = f"{self.EW_API}/{self.content_id}"
        res = requests.get(url, headers=headers)
        return res.json()

    def pool_ew(self):
        ew_ongoing = True

        while ew_ongoing:
            json_response = self.edgeware_check()
            logger.debug(json.dumps(json_response, indent=4))

            if json_response["state"] in ["error"]:
                self.ew.msg = json_response
                self.ew.status = self.ew.Status.EW_ERROR
                self.ew.save()
                ew_ongoing = json_response["state"] == "ongoing"

            sleep(5)

        logger.info("DONE")

    # Function to call Edgeware API and extract the "dash" URL
    def edgeware_create(self):
        logger.info(f"Calling Edgeware API with content_id: {self.content_id}")
        payload = {
            "service": "HTTP",
            "source": "upload",
            "content_id": self.content_id,
            "title": self.title,
            "upload": {
                "location": f"file:///mnt/storage-lj/{self.ftp_folder}/manifest.mpd"
            },
        }
        headers = {"x-account-api-key": self.EW_KEY}

        res = requests.post(self.EW_API, json=payload, headers=headers)
        self.ew.status = self.ew.Status.EW_PENDIND

        self.ew.msg = res.json()
        self.ew.content_id = self.content_id

        for key, uri in res.json()["delivery_uris"].items():
            DeliveryUri.objects.create(type=key, uri=uri, ew=self.ew)

        self.ew.save()

    def _upload_directory(self, ftp, local_dir: Path, remote_dir):
        """Recursively upload a directory to an FTP server."""
        # Ensure remote directory exists
        try:
            ftp.mkd(remote_dir)
            logger.info(f"Created remote ftp dir: {remote_dir}")

        except ftplib.error_perm:
            logger.info(f"Directory already exist: {remote_dir}")
            pass

        ftp.cwd(remote_dir)
        logger.info(f"FTP set cwd: {remote_dir}")

        # Iterate through local directory
        for item in local_dir.iterdir():
            # local_path = os.path.join(local_dir, item)

            if item.is_file() and item.suffix in [".mp4", ".mpd"]:
                # Upload file
                logger.info(f"Uploading file: {item}")
                with open(item, "rb") as file:
                    ftp.storbinary(f"STOR {item.name}", file)

            # elif os.path.isdir(local_path):
            #     # Recursively upload directory
            #     logger.info(f"Entering directory: {local_path}")
            #     self._upload_directory(ftp, item, item)

        # Move back to parent directory
        ftp.cwd("..")

    def ftp_upload_dir(self):
        """Connect to FTP server and upload directory."""
        try:
            # Connect to FTP server
            ftp = ftplib.FTP(self.FTP_HOST)
            ftp.login(self.FTP_USER, self.FTP_PASS)
            logger.info(f"Connected to {self.FTP_HOST}")

            # Upload directory
            self._upload_directory(ftp, self.src_dir, self.ftp_folder)

            # Close connection
            ftp.quit()
            logger.info("Upload completed successfully")
            self.ew.status = self.ew.Status.FTP_UPLOAD

        except ftplib.all_errors as e:
            logger.exception(f"FTP error: {e}")
            self.ew.status = self.ew.Status.FTP_ERROR
        except Exception as e:
            logger.exception(f"Error: {e}")
            self.ew.status = self.ew.Status.FTP_ERROR
        finally:

            self.ew.save()

    def publish(self):

        self.ftp_upload_dir()
        self.edgeware_create()
        self.pool_ew()


def fetch_rabbitmq_queues():
    url = 'http://bpl-vidra-03.ts.telekom.si:15672/'
    user = 'guest'
    password = 'guest'

    try:
        response = requests.get(url, auth=HTTPBasicAuth(user, password))
        response.raise_for_status()
        data = response.json()

        queues = []
        for q in data:
            queues.append({
                'queue': q['name'],
                'messages': q.get('messages', 0),
                'unacked': q.get('messages_unacknowledged', 0),
                'ready': q.get('messages_ready', 0),
                'consumers': q.get('consumers', 0),
                'idle_since': q.get('idle_since', 'N/A'),
                'status': 'success' if q.get('consumers', 0) > 0 else 'warning',
            })

        return queues

    except Exception as e:
        return [{
            'queue': 'ERROR',
            'messages': 'N/A',
            'unacked': 'N/A',
            'ready': 'N/A',
            'consumers': 'N/A',
            'idle_since': str(e),
            'status': 'error',
        }]
