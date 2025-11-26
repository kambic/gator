from datetime import datetime
from pathlib import Path
from typing import Dict, List

from rich.progress import Progress, TextColumn, BarColumn, TransferSpeedColumn, TimeRemainingColumn


class CopyWithProgress:
    def __init__(self, chunk_size=1024 * 1024):
        self.chunk_size = chunk_size

    def copy(self, src: Path, dest: Path):
        src = Path(src)
        dest = Path(dest)

        total_size = src.stat().st_size

        with src.open("rb") as src_file, dest.open("wb") as dest_file, Progress(
                TextColumn("[bold blue]Copying[/bold blue] {task.fields[filename]}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
        ) as progress:

            task = progress.add_task("copy", filename=src.name, total=total_size)

            while True:
                chunk = src_file.read(self.chunk_size)
                if not chunk:
                    break
                dest_file.write(chunk)
                progress.update(task, advance=len(chunk))


class ProviderFileInspector:
    def __init__(self, provider: str, root: str = "/export/isilj/fenix2"):
        self.provider = provider
        self.root = Path(root)

        self.search_roots = {
            'failed': self.root / "FAILED" / provider,
            'upload': self.root / "UPLOAD" / provider,
            'enqueued': self.root / provider,
        }

    def locate_files(self, pattern: str = "*.tar", recursive: bool = False, enqueued=False) -> Dict[str, List[Path]]:
        """
        Locate files matching the given pattern in all search roots.

        Args:
            pattern: Glob pattern for matching files (e.g., '*.tar', '*.mp4').
            recursive: Whether to search recursively.

        Returns:
            Dictionary mapping search root keys to lists of Path objects for matching files.
        """
        matches = {'failed': [], 'upload': [],'enqueued' : []}

        if enqueued:
            matches['enqueued'] = []

        for key, path in self.search_roots.items():
            if not path.exists():
                continue
            if recursive:
                matches[key].extend(path.rglob(pattern))
            else:
                matches[key].extend(path.glob(pattern))
            matches[key].sort()
        return matches

    def _format_size(self, size_bytes: int) -> str:
        """Return a human-readable file size (e.g. '1.23 MB')."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def summary(self, pattern: str = "*.tar", recursive: bool = False) -> None:
        """Print a concise summary of matched files with metadata."""
        files = self.locate_files(pattern, recursive)
        total_files = sum(len(file_list) for file_list in files.values())
        print(f"Provider: {self.provider}, Total files: {total_files}")
        for key, file_list in files.items():
            if file_list:
                print(f"{key.capitalize()}:")
                for f in file_list:
                    stat = f.stat()
                    size = self._format_size(stat.st_size)
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"  {f.name} | {size} | {mtime}")


inspector = ProviderFileInspector("blitz")
files = inspector.locate_files(pattern="*.tar", recursive=True)
copier = CopyWithProgress()
