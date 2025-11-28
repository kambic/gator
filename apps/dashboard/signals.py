import structlog as logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.dashboard.models import Edgeware

# from video_encoding import tasks

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Edgeware)
def job_post_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"[NEW] Job created: {instance.status}")
    else:
        logger.info(f"[UPDATED] Job updated: {instance.status}")
