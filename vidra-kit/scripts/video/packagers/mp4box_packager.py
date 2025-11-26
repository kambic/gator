from .abstract_packager import AbstractPackager
from typing import Dict, Any, List, Callable
import os


class MP4BoxPackager(AbstractPackager):
    """
    GPAC MP4Box-based DASH packager.
    Assumes MP4Box is installed and in PATH.
    """

    def package(
        self,
        input_dir: str,
        output_dir: str,
        progress_callback: Callable[[float], None] = None,
    ) -> bool:
        """
        Packages MP4 files in input_dir to DASH using MP4Box.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Example: Dash setup for input files
        cmd = [
            "MP4Box",
            "-dash",
            "4000",  # 4s fragments
            "-frag",
            "4000",
            "-rap",
            "-profile",
            "live",
            "-out",
            f"{output_dir}/dash.mpd",
            f"{input_dir}/*.mp4",
        ]

        # Extend with config
        if "fragment_duration" in self.config:
            cmd[2] = f"-dash {self.config['fragment_duration']}"

        success = self._run_command(cmd, progress_callback)
        return success
