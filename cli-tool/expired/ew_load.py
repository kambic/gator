import json
from pathlib import Path

import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()
from apps.dashboard.models import Edgeware,  Stream
import loguru



from django.utils import timezone
from datetime import datetime
tz = timezone.get_current_timezone()


mtcms_stag = Path('mtcms_stag_response.json')
with open(mtcms_stag) as f:
    mtcms_stag = json.load(f)
    print(len(mtcms_stag))


for items in mtcms_stag:
    offer_id = items.get('mappedOfferId')
    expired = items.get('expired')
    expired = datetime.fromisoformat(expired,)
    for uri in items['videoURLs']:
        uri  = uri['videoURL']
        if uri.startswith('rtsp'):
            continue
        uri = uri.split('/')
        if len(uri) < 9:
            continue

        hit = Stream.objects.filter(uri__contains=uri[10])
        if hit.exists():
            hit = hit.first()
            ew = hit.edge
            ew.offer_id = offer_id
            ew.expired = expired
            ew.mtcms_stag = True
            ew.save()
            loguru.logger.info(f"Hit for {ew.ew_id} found")
            break

            # input()
