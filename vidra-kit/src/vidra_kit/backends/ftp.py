from ftplib import FTP, error_perm
from datetime import datetime
from typing import List, Dict, Generator, Optional
import logging

logger = logging.getLogger(__name__)


class FtpAgent:
    """
    Context-manager based FTP client for scanning remote directories and files.
    Automatically connects on enter and disconnects on exit.
    """

    # Directories or patterns to skip during scan
    SKIP_PATTERNS = {".snapshot", ".snapshots", "__MACOSX", ".DS_Store"}

    def __init__(
        self,
        host: str,
        user: str = "anonymous",
        passwd: str = "anonymous@",
        port: int = 21,
        timeout: int = 30,
        encoding: str = "utf-8",
    ):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.timeout = timeout
        self.encoding = encoding

        self._ftp: Optional[FTP] = None

    def __enter__(self):
        """Connect and login to FTP server when entering context"""
        try:
            self._ftp = FTP(timeout=self.timeout, encoding=self.encoding)
            self._ftp.connect(host=self.host, port=self.port)
            self._ftp.login(user=self.user, passwd=self.passwd)

            logger.info(f"Successfully connected to ftp://{self.host}")
            return self
        except Exception as e:
            raise ConnectionError(f"Failed to connect to FTP {self.host}: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Safely close connection on exit"""
        if self._ftp:
            try:
                self._ftp.quit()
            except:
                try:
                    self._ftp.close()
                except:
                    pass
            self._ftp = None
        if exc_type:
            logger.error(f"FTP session ended with error: {exc_val}")

    # ------------------------------------------------------------------
    # Public scanning methods
    # ------------------------------------------------------------------

    def list_dir(self, remote_path: str = "") -> List[Dict[str, str]]:
        """
        List all files and directories in the given remote path (MLSD preferred, fallback to LIST)
        Returns list of dicts with keys: name, type, size, modify, etc.
        """
        if not self._ftp:
            raise RuntimeError("FTP connection not established. Use 'with' statement.")

        path = remote_path or "."
        entries = []

        try:
            # MLSD is modern, structured, and reliable (preferred)
            for name, facts in self._ftp.mlsd(path=path):
                if self._should_skip(name):
                    continue

                entry = {
                    "name": name,
                    "path": f"{path}/{name}".replace("//", "/").strip("/"),
                    "type": facts.get("type"),  # file, dir, cdir, pdir
                    "size": int(facts["size"]) if "size" in facts else None,
                    "modify": self._parse_ftp_time(facts.get("modify")),
                    "perm": facts.get("perm"),
                    "unix.mode": facts.get("unix.mode"),
                    "unix.owner": facts.get("unix.owner"),
                    "unix.group": facts.get("unix.group"),
                }
                entries.append(entry)
        except error_perm:
            # Fallback to classic LIST parsing if MLSD not supported
            logger.warning("MLSD not supported, falling back to LIST parsing")
            entries = self._parse_list_output(path)

        return entries

    def walk(self, top: str = ".") -> Generator[tuple[str, List[Dict], List[Dict]], None, None]:
        """
        Recursively walk FTP directory tree (like os.walk).
        Yields (dirpath, dirs, files) for each directory.
        """
        dirs = []
        files = []

        for entry in self.list_dir(top):
            if entry["type"] == "dir" or entry["type"] in ("cdir", "pdir"):
                if entry["name"] not in {".", ".."}:
                    dirs.append(entry)
            else:
                files.append(entry)

        yield top, dirs, files

        for dir_entry in dirs:
            subpath = f"{top}/{dir_entry['name']}".replace("//", "/")
            yield from self.walk(subpath)

    def find_files(
        self,
        remote_path: str = ".",
        name_pattern: str = "*",
        recursive: bool = True,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        newer_than: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Search for files matching criteria.
        Supports glob-like name_pattern (simple wildcard * only).
        """
        results = []

        def matches(name: str) -> bool:
            if name_pattern == "*" or name_pattern == "":
                return True
            if name_pattern.startswith("*") and name_pattern.endswith("*"):
                return name_pattern[1:-1] in name
            if name_pattern.startswith("*"):
                return name.endswith(name_pattern[1:])
            if name_pattern.endswith("*"):
                return name.startswith(name_pattern[:-1])
            return name == name_pattern

        iterator = self.walk(remote_path) if recursive else [ (remote_path, [], self.list_dir(remote_path)) ]

        for dirpath, _, files in iterator:
            for f in files:
                if f["type"] != "file":
                    continue
                if not matches(f["name"]):
                    continue
                if min_size is not None and (f["size"] is None or f["size"] < min_size):
                    continue
                if max_size is not None and (f["size"] is not None and f["size"] > max_size):
                    continue
                if newer_than and (f["modify"] is None or f["modify"] < newer_than):
                    continue

                results.append(f)

        return results

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    def _should_skip(self, name: str) -> bool:
        return any(skip in name for skip in self.SKIP_PATTERNS) or name.startswith(".")

    def _parse_ftp_time(self, timestr: Optional[str]) -> Optional[datetime]:
        if not timestr:
            return None
        # MLSD modify format: YYYYMMDDHHmmSS[.sss]
        try:
            return datetime.strptime(timestr.split(".")[0], "%Y%m%d%H%M%S")
        except:
            return None




    def _parse_list_output(self, path: str) -> List[Dict]:
        """Fallback parsing of traditional LIST command output"""
        lines = []
        self._ftp.dir(path, lines.append)
        entries = []
        for line in lines:
            parts = line.split(None, 8)
            if len(parts) < 9:
                continue
            name = parts[8]
            if self._should_skip(name) or name in {".", ".."}:
                continue

            is_dir = parts[0].startswith("d")
            size = int(parts[4]) if not is_dir and parts[4].isdigit() else None

            # Parse date/time (simplified)
            try:
                mod_time = datetime.strptime(f"{parts[5]} {parts[6]} {parts[7]}", "%b %d %H:%M" if ":" in parts[7] else "%b %d %Y")
                mod_time = mod_time.replace(year=datetime.now().year if mod_time.year > datetime.now().year else mod_time.year)
            except:
                mod_time = None

            entries.append({
                "name": name,
                "path": f"{path}/{name}".replace("//", "/").strip("/"),
                "type": "dir" if is_dir else "file",
                "size": size,
                "modify": mod_time,
            })
        return entries


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    with FtpAgent(host="isilj.ts.telekom.si", user="ftpott", passwd="") as ftp:

        print("Root directory contents:")
        for entry in ftp.list_dir():
            print(f"{entry['type'][:3]:<4} {entry['size'] or '-':>10} {entry['modify']}  {entry['name']}")

        # print("\nAll .txt files under 1MB:")
        # txt_files = ftp.find_files(name_pattern="*.txt", max_size=1024*1024)
        # for f in txt_files[:10]:
        #     print(f"  {f['size']/1024:6.1f} KB  {f['path']}")
