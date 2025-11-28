# api/client.py (minimal version)
import uuid, requests
from yourapp.models import Content
from django.utils.timezone import now


class ContentAPIClient:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def sync_all(self, limit: int = None):
        page = 1
        total = created = updated = 0

        while True:
            items = self.session.get(f"{self.base_url}/contents", params={"page": page, "per_page": 200}).json().get("results") or []
            if not items:
                break

            for item in items:
                if limit and total >= limit:
                    break

            if len(items) < 200 or (limit and total >= limit):
                break
            page += 1

        print(f"Done → {created} created, {updated} updated, {total} total")
