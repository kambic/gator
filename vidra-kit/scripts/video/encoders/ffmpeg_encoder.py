import subprocess
import re
import os
from typing import Callable, Optional
from .abstract_encoder import AbstractEncoder


class FFmpegEncoder(AbstractEncoder):
    """
    FFmpeg-based encoder for transcoding to MP4 or TS.
    Supports progress callbacks via ffmpeg's -progress pipe.
    """

    def encode(
        self,
        input_file: str,
        output_file: str,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> bool:
        """
        Transcodes using FFmpeg and reports progress if callback provided.
        """
        # Probe duration first (so we can estimate percentage)
        duration = self._get_duration(input_file)
        if duration is None:
            print("⚠️ Could not determine input duration; progress will be unavailable.")

        cmd = [
            "ffmpeg",
            "-i",
            input_file,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-y",
            output_file,
        ]

        if "video_bitrate" in self.config:
            cmd.extend(["-b:v", self.config["video_bitrate"]])

        if output_file.endswith(".ts"):
            cmd.extend(["-f", "mpegts"])

        # Add a pipe for progress output
        progress_pipe = subprocess.PIPE
        ffmpeg_proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
        )

        if not progress_callback:
            ffmpeg_proc.wait()
            return ffmpeg_proc.returncode == 0

        time_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")

        # Read ffmpeg output line by line
        for line in ffmpeg_proc.stderr:
            match = time_pattern.search(line)
            if match and duration:
                current_time = self._time_to_seconds(match.group(1))
                progress = min(current_time / duration, 1.0)
                progress_callback(progress)

        ffmpeg_proc.wait()
        return ffmpeg_proc.returncode == 0

    # --------------------------
    # Helpers
    # --------------------------

    def _get_duration(self, filename: str) -> Optional[float]:
        """Get duration (in seconds) using ffprobe."""
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    filename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return float(result.stdout.strip())
        except Exception:
            return None

    def _time_to_seconds(self, timestr: str) -> float:
        """Convert HH:MM:SS.xx → seconds."""
        h, m, s = timestr.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
