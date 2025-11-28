# your_app/management/commands/scan_folder.py
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import FileNode  # ← change to your actual app name


"""
# Basic scan (create/update only)
python manage.py scan_folder "/home/user/Documents/MyProjectFiles" --root-name "Project Files"

# With delete missing files/folders
python manage.py scan_folder "./media/user_uploads/123" --root-name "My Files" --delete

# Relative path example
python manage.py scan_folder ../real_folder --root-name "Backup"

"""


class Command(BaseCommand):
    help = "Scan a real folder and sync it into FileNode database (creates/updates folders & files)"

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            type=str,
            help="Absolute or relative path to the folder to scan (e.g. /home/user/MyFiles or ./media/files)",
        )
        parser.add_argument(
            "--root-name",
            type=str,
            default="My Files",
            help="Name of the root node in DB (default: My Files)",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete nodes from DB that no longer exist on disk",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        scan_path = Path(options["path"]).resolve()
        if not scan_path.exists():
            self.stderr.write(self.style.ERROR(f"Path does not exist: {scan_path}"))
            return

        root_name = options["root_name"]
        should_delete = options["delete"]

        self.stdout.write(f"Scanning: {scan_path}")
        self.stdout.write(f"Root node name: {root_name}")
        self.stdout.write(f"Delete missing: {should_delete}")

        # Get or create root node
        root_node, created = FileNode.objects.get_or_create(
            parent=None,
            name=root_name,
            defaults={"is_folder": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created root node: {root_name}"))

        # Track what we see on disk this run
        seen_paths = set()

        def sync_directory(current_node: FileNode, current_path: Path):
            if not current_path.is_dir():
                return

            # Get current children from filesystem
            try:
                disk_items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                self.stdout.write(self.style.WARNING(f"Permission denied: {current_path}"))
                return

            # Map existing DB children by name
            db_children = {child.name: child for child in current_node.children.all()}

            for item in disk_items:
                seen_paths.add(item.resolve())

                is_folder = item.is_dir()
                node_name = item.name

                if node_name.startswith("."):  # skip hidden files/folders
                    continue

                if is_folder:
                    node, created = FileNode.objects.get_or_create(
                        parent=current_node,
                        name=node_name,
                        defaults={"is_folder": True},
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created folder → {node.get_full_path()}"))
                    else:
                        # Update in case renamed manually in DB
                        if node.name != node_name:
                            node.name = node_name
                            node.save()
                else:
                    # File
                    defaults = {
                        "is_folder": False,
                        "file_size": item.stat().st_size,
                    }
                    node, created = FileNode.objects.update_or_create(
                        parent=current_node,
                        name=node_name,
                        defaults=defaults,
                    )
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"{action} file → {node.get_full_path()} ({node.file_size} bytes)")

                # Recurse into folders
                if is_folder:
                    sync_directory(node, item)

        # Start recursion
        sync_directory(root_node, scan_path)

        # Optional: delete nodes that disappeared from disk
        if should_delete:
            deleted_count = 0
            for node in FileNode.objects.filter(parent=root_node).iterator():
                expected_path = scan_path / node.get_full_path().replace(root_name, "", 1).lstrip("/")
                if not Path(expected_path).resolve() in seen_paths:
                    full_path = node.get_full_path()
                    node.delete()
                    deleted_count += 1
                    self.stdout.write(self.style.WARNING(f"Deleted missing → {full_path}"))
            if deleted_count:
                self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} missing items"))

        self.stdout.write(self.style.SUCCESS("Folder scan & sync completed successfully!"))
