import asyncio
from timeit import timeit

import aiohttp
import django
import os
import loguru
import requests

logger = loguru.logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.dashboard.models import Edgeware, Stream


class EdgeWareAPI:
    EW_KEY = "wgXfC6EHEAjQt8wvzErgRE"
    EW_API = "http://ew-api.tv.telekom.si:8090/api/2/content"
    EW_SECRET = "kdmgj7390s"

    def __init__(self, ew) -> None:
        self.ew = ew

    def edgeware_check(self):
        headers = {"x-account-api-key": self.EW_KEY}
        url = f"{self.EW_API}/{self.ew.ew_id}"
        res = requests.get(url, headers=headers)
        try:
            self.update_state_in_db(res.json())
        except Exception:
            logger.exception(f"Failed to update {ew.ew_id}")
        return

    def update_state_in_db(self, data: dict):
        data_dict = {
            "title": data["title"],
            "status": data["state"],
            "playable": data["playable"],
            "content_duration_ms": data["content_duration_ms"],
            "msg": data["additional_state_info"],
            "created": data["creation_time"],
            "modified": data["modification_time"],
            "ftp_dir": data["upload"]['location'],
        }

        for key, value in data_dict.items():
            setattr(self.ew, key, value)
        self.ew.ew_dump_loaded = True
        self.ew.save()
        # updated += 1
        delivery_uris = data["delivery_uris"]
        for key, val in delivery_uris.items():
            setattr(self.ew, key, val)
            Stream.objects.create(
                edge=self.ew, uri=val, type=key)

        logger.info(f"Updated {self.ew.ew_id}")


edges = Edgeware.objects.filter(ew_dump_loaded=False)[:10000]

for ew in edges:
    api = EdgeWareAPI(ew)
    api.edgeware_check()
