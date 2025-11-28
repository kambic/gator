import ftplib
import logging
from time import sleep
from uuid import uuid4

from django.conf import settings
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Optional, Dict, Any
import uuid


class EdgewareAPIError(Exception):
    """Custom exception for Edgeware API errors"""

    pass


class EdgewareApi:
    EW_KEY = "wgXfC6EHEAjQt8wvzErgRE"
    EW_API = "http://ew-api.tv.telekom.si:8090/api/2"
    OFFSET = 0
    LIMIT = 1000
    TOTAL = None

    def __init__(self, offset=None, content_id: Optional[str] = None) -> None:
        if offset is not None:
            self.OFFSET = offset
        self.content_id = content_id or str(uuid.uuid4())

        # Default headers with API key
        self.headers = {"x-account-api-key": self.EW_KEY}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.EW_API.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            if response.status_code == 401:
                raise EdgewareAPIError("Unauthorized - invalid API key")
            if response.status_code == 403:
                raise EdgewareAPIError("Forbidden")
            if not response.ok:
                raise EdgewareAPIError(f"HTTP {response.status_code}: {response.text}")
            return response.json()
        except requests.RequestException as e:
            raise EdgewareAPIError(f"Request failed: {e}")

    def check_content(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check status of a specific content by ID
        """
        cid = content_id or self.content_id

        cid = content_id or self.content_id
        return self._get(f"/{cid}")

    def list_content_page(self, limit: int = 100, offset: int = 0, **filters):
        """Fetch one page"""
        params = {"limit": limit, "offset": offset, "source": "upload"}
        params.update(filters)
        return self._get("content", params=params)

    def get_content_by_id(self, content_id: str) -> Dict[str, Any]:

        return self._get(f"/{content_id}")

    def search_content(self, query: str, **params) -> Dict[str, Any]:

        params["q"] = query
        return self._get("/content", params=params)

    def next_page(self):
        data = self.list_content_page(limit=self.LIMIT, offset=self.OFFSET)
        content = data.get("content", [])
        self.TOTAL = data.get("total")  # use real total from API
        self.OFFSET += self.LIMIT
        return content

    @property
    def has_next_page(self):
        if self.TOTAL is None:
            return True
        return self.OFFSET < self.TOTAL


class Pager:
    LIMIT = 100

    def __init__(self):
        self.OFFSET = 0
        self.TOTAL = self.LIMIT
        self._last_page = None

    def list_content_page(self, limit, offset):
        """
        Replace with your API call.
        Must return: {"content": [...items...] }
        """
        raise NotImplementedError

    def next_page(self):
        data = self.list_content_page(limit=self.LIMIT, offset=self.OFFSET)
        content = data.get("content", [])

        self.TOTAL = len(content)
        self.OFFSET += self.LIMIT
        self._last_page = content

        return content

    @property
    def has_next_page(self):
        return self.TOTAL == self.LIMIT

    def load_batch(self, batch_size: int):
        """
        Load `batch_size` pages in a single call.
        Returns combined items.
        """
        batch = []

        for _ in range(batch_size):
            page = self.next_page()
            if not page:
                break
            batch.extend(page)

        return batch


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
    url = "http://bpl-vidra-03.ts.telekom.si:15672/"
    user = "guest"
    password = "guest"

    try:
        response = requests.get(url, auth=HTTPBasicAuth(user, password))
        response.raise_for_status()
        logger.info(response.text)
        data = response.json()

        queues = []
        for q in data:
            queues.append(
                {
                    "queue": q["name"],
                    "messages": q.get("messages", 0),
                    "unacked": q.get("messages_unacknowledged", 0),
                    "ready": q.get("messages_ready", 0),
                    "consumers": q.get("consumers", 0),
                    "idle_since": q.get("idle_since", "N/A"),
                    "status": "success" if q.get("consumers", 0) > 0 else "warning",
                }
            )

        return queues

    except Exception as e:
        logger.exception(e)
        return [
            {
                "queue": "ERROR",
                "messages": "N/A",
                "unacked": "N/A",
                "ready": "N/A",
                "consumers": "N/A",
                "idle_since": str(e),
                "status": "error",
            }
        ]


import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json


@dataclass
class RabbitMQQueue:
    name: str
    vhost: str
    messages: int
    messages_ready: int
    messages_unacknowledged: int
    consumers: int
    state: str
    message_stats: Dict[str, Any]

    def __str__(self):
        return (
            f"{self.vhost}/{self.name} | "
            f"Total: {self.messages} | "
            f"Ready: {self.messages_ready} | "
            f"Unack: {self.messages_unacknowledged} | "
            f"Consumers: {self.consumers} | "
            f"State: {self.state}"
        )


class RabbitMQMonitor:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 15672,
        username: str = "guest",
        password: str = "guest",
        vhost: str = "/",
        verify_ssl: bool = True,
        timeout: int = 10,
    ):
        self.base_url = f"http://{host}:{port}/api"
        self.auth = (username, password)
        self.vhost_encoded = requests.utils.quote(vhost, safe="")
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})
        if not verify_ssl:
            self.session.verify = False

    def _get(self, endpoint: str, params=None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        resp = self.session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_overview(self) -> Dict:
        """Get cluster overview (message rates, connections, etc.)"""
        return self._get("/overview")

    def get_all_queues(self) -> List[RabbitMQQueue]:
        """Return list of all queues with key stats"""
        queues = self._get("/queues")
        result = []
        for q in queues:
            result.append(
                RabbitMQQueue(
                    name=q.get("name", ""),
                    vhost=q.get("vhost", ""),
                    messages=q.get("messages", 0),
                    messages_ready=q.get("messages_ready", 0),
                    messages_unacknowledged=q.get("messages_unacknowledged", 0),
                    consumers=q.get("consumers", 0),
                    state=q.get("state", "unknown"),
                    message_stats=q.get("message_stats", {}),
                )
            )
        return result

    def get_queue(self, queue_name: str, vhost: str = "/") -> Optional[RabbitMQQueue]:
        """Get single queue details"""
        vhost_encoded = requests.utils.quote(vhost, safe="")
        try:
            data = self._get(f"/queues/{vhost_encoded}/{queue_name}")
            return RabbitMQQueue(
                name=data.get("name", queue_name),
                vhost=data.get("vhost", vhost),
                messages=data.get("messages", 0),
                messages_ready=data.get("messages_ready", 0),
                messages_unacknowledged=data.get("messages_unacknowledged", 0),
                consumers=data.get("consumers", 0),
                state=data.get("state", "unknown"),
                message_stats=data.get("message_stats", {}),
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Queue {queue_name} not found in vhost {vhost}")
                return None
            raise

    def print_queues(self, filter_celery: bool = True):
        """Pretty print all queues (Flower-style)"""
        queues = self.get_all_queues()
        if filter_celery:
            queues = [
                q
                for q in queues
                if "celery" in q.name or q.consumers > 0 or q.messages > 0
            ]

        print(
            f"{'Vhost':<10} {'Queue':<30} {'Total':>8} {'Ready':>8} {'Unack':>8} {'Consumers':>10} {'State':<8}"
        )
        print("-" * 85)
        for q in sorted(queues, key=lambda x: (x.vhost, x.name)):
            print(
                f"{q.vhost:<10} {q.name:<30} "
                f"{q.messages:>8} {q.messages_ready:>8} {q.messages_unacknowledged:>8} "
                f"{q.consumers:>10} {q.state:<8}"
            )
