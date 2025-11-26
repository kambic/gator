from .abstract_packager import AbstractPackager
from typing import Dict, Any, List, Callable


class Bento4Packager(AbstractPackager):
    """
    Bento4-based DASH packager.
    Assumes Bento4 tools (MP4Fragment, MP4Dash) are installed and in PATH.
    """

    def package(
        self,
        input_dir: str,
        output_dir: str,
        progress_callback: Callable[[float], None] = None,
    ) -> bool:
        """
        Packages MP4 files in input_dir to DASH using Bento4.
        """
        # Fragment MP4 files
        cmd_fragment = [
            "MP4Fragment",
            "--use-segment-timeline",
            "--time-scale=90000",
            f"{input_dir}/*.mp4",
            f"{output_dir}/frag",
        ]
        if not self._run_command(
            cmd_fragment,
            lambda p: progress_callback(p * 0.3) if progress_callback else None,
        ):
            return False

        # Generate DASH MPD
        cmd_dash = [
            "MP4Dash",
            "--use-segment-timeline",
            "--time-scale=90000",
            "--min-buffer=2",
            "--media-source-duration=0",
            f"{output_dir}/frag/*.m4s",
            "-out",
            f"{output_dir}/dash.mpd",
            "-f",
        ]
        success = self._run_command(
            cmd_dash,
            lambda p: progress_callback(30 + p * 0.7) if progress_callback else None,
        )

        return success
