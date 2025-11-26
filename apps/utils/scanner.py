import os
from ftplib import FTP, error_perm
from datetime import datetime
from django.utils import timezone
from apps.dashboard.models import FileEntry


class TreeScanner:
    skip = [".snapshot"]

    def __init__(self, parent=None):
        self.parent = parent

    # ----------------------------
    # Save or update a DB entry
    # ----------------------------
    def save_entry(self, name, path, entry_type, size=None, modified=None):
        if modified and timezone.is_naive(modified):
            modified = timezone.make_aware(modified, timezone.get_current_timezone())

        obj, _ = FileEntry.objects.update_or_create(
            path=path,
            defaults={
                "name": name,
                "entry_type": entry_type,
                "parent": self.parent,
                "size": size,
                "modified": modified,
            },
        )
        return obj

    # ----------------------------
    # Local filesystem scanning
    # ----------------------------
    def scan_local(self, path):
        path = os.path.abspath(path)
        name = os.path.basename(path) or path

        if name in self.skip:
            return

        # Build a set of current entries under this directory
        if os.path.isdir(path):
            current_children_paths = set()
            for item in os.listdir(path):
                current_children_paths.add(os.path.join(path, item))

            obj = self.save_entry(name, path, "dir")

            # Recurse
            for item_path in current_children_paths:
                TreeScanner(parent=obj).scan_local(item_path)

            # Remove deleted children from DB
            self._cleanup_deleted(obj, current_children_paths)

        else:
            size = os.path.getsize(path)
            modified = timezone.make_aware(
                datetime.fromtimestamp(os.path.getmtime(path)),
                timezone.get_current_timezone(),
            )
            self.save_entry(name, path, "file", size, modified)

    # ----------------------------
    # FTP scanning
    # ----------------------------
    def scan_ftp(self, host, user="anonymous", passwd="anonymous@", remote_path=""):
        with FTP(host) as ftp:
            ftp.login(user, passwd)
            print(f"Connected to {host}")
            self._scan_ftp_list(ftp, remote_path)
            # self._scan_ftp_tree(ftp, remote_path)

    def _scan_ftp_tree(self, ftp: FTP, path=""):
        ftp.cwd(path or "/")
        try:
            current_children_paths = set()
            try:
                # MLSD
                for name, facts in ftp.mlsd():
                    if name in (".", ".."):
                        continue

                    entry_type = "dir" if facts.get("type") == "dir" else "file"
                    full_path = f"{path}/{name}" if path else name
                    current_children_paths.add(full_path)

                    size = int(facts.get("size", 0)) if entry_type == "file" else None
                    modified = None
                    if "modify" in facts:
                        try:
                            naive_dt = datetime.strptime(
                                facts["modify"], "%Y%m%d%H%M%S"
                            )
                            modified = timezone.make_aware(
                                naive_dt, timezone.get_current_timezone()
                            )
                        except ValueError:
                            pass

                    obj = TreeScanner(parent=self.parent).save_entry(
                        name, full_path, entry_type, size, modified
                    )

                    if entry_type == "dir":
                        TreeScanner(parent=obj)._scan_ftp_tree(ftp, full_path)

            except error_perm as e:
                if "MLSD" in str(e):
                    current_children_paths = self._scan_ftp_list(ftp, path)
                else:
                    print(f"[ERROR] Cannot access {path}: {e}")

            # Clean up deleted entries
            if self.parent:
                self._cleanup_deleted(self.parent, current_children_paths)

        except error_perm as e:
            print(f"[ERROR] Cannot access {path}: {e}")

    def _scan_ftp_list(self, ftp: FTP, path=""):
        entries = []
        ftp.retrlines(f"LIST {path}", entries.append)
        current_children_paths = set()

        for entry in entries:
            parts = entry.split(maxsplit=8)
            if len(parts) < 9:
                continue
            perms, _, _, _, size, month, day, time_or_year, name = parts
            full_path = f"{path}/{name}" if path else name
            current_children_paths.add(full_path)

            if perms.startswith("d"):
                obj = TreeScanner(parent=self.parent).save_entry(name, full_path, "dir")
                try:
                    TreeScanner(parent=obj)._scan_ftp_list(ftp, full_path)
                except error_perm:
                    pass
            else:
                self.save_entry(name, full_path, "file", int(size))

        return current_children_paths

    # ----------------------------
    # Remove DB entries that no longer exist
    # ----------------------------
    def _cleanup_deleted(self, parent_obj, current_paths_set):
        """
        Delete or prune children in DB that are no longer present in current scan.
        """
        for child in parent_obj.get_children():
            if child.path not in current_paths_set:
                child.delete()
