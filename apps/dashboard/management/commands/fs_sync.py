import json
import os

from django.core.files import File as DjangoFile
from django.core.management.base import BaseCommand
from filer.models import Image, File, Folder  # Or use Image for images only

class Command(BaseCommand):
    help = "Bulk upload files to django-filer from a directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory_path", type=str, help="Path to directory with files"
        )
        parser.add_argument(
            "--folder-name",
            type=str,
            default="Imported Files",
            help="Target folder name",
        )

    def handle(self, *args, **options):
        directory = options["directory_path"]
        folder_name = options["folder_name"]


    def scan_folders(self, directory, folder_name,):


        # Create or get target folder
        folder, created = Folder.objects.get_or_create(name=folder_name, parent=None)

        uploaded_count = 0
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "rb") as f:
                        django_file = DjangoFile(f, name=filename)

                        # For images (use File for non-images)
                        if filename.lower().endswith(
                                (".png", ".jpg", ".jpeg", ".gif", ".webp")
                        ):
                            obj = Image.objects.create(file=django_file, folder=folder)
                        else:
                            obj = File.objects.create(file=django_file, folder=folder)

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully uploaded {filename}")
                    )
                    uploaded_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error uploading {filename}: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Uploaded {uploaded_count} files to folder "{folder_name}"'
            )
        )
