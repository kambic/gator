from datetime import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from vidra_kit.storage.islon import ProviderFileInspector

from apps.dashboard.models import Packet, Provider


# from apps.mediahub.models import VODProvider, Packet


class Command(BaseCommand):
    help = "Inspect provider"

    def add_arguments(self, parser):
        parser.add_argument(
            "provider",
            type=str,
            help="Inspect provider in fenix labirint",
        )

    def handle(self, provider, *args, **options):

        provider = Provider.objects.get(user__username=provider)

        inspector = ProviderFileInspector(provider.user.username)
        files = inspector.locate_files(pattern="*.tar", recursive=True)

        for status, files in files.items():
            for f in files:
                stats = f.stat()
                delivery_time = timezone.localtime(
                    timezone.make_aware(datetime.fromtimestamp(stats.st_ctime))
                )
                defaults = {
                    'status': status,
                    'delivery_time': delivery_time,
                    'title': f.name,
                    'size' : stats.st_size,
                }

                packet, created = Packet.objects.update_or_create(
                    provider=provider,
                    file=f,
                    defaults=defaults,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found package in {status} for {provider} and create item in db for {packet.file}"
                    )
                )

    def collect_metadata(self):
        self.stdout.write(self.style.SUCCESS("Collecting metadata..."))
