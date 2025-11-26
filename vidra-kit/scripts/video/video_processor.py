from typing import Dict, Any, Optional, Union
from tqdm import tqdm
import os
from .encoders import FFmpegEncoder
from .packagers import Bento4Packager, MP4BoxPackager
from .encoders.abstract_encoder import AbstractEncoder
from .packagers.abstract_packager import AbstractPackager


class VideoProcessor:
    """
    Main class to load encoder/packager and run the encoding/transcoding pipeline.
    Supports modular selection of encoder and packager.
    """

    def __init__(self, encoder_config: Dict[str, Any], packager_config: Dict[str, Any]):
        self.encoder = self._load_encoder(encoder_config)
        self.packager = self._load_packager(packager_config)

    def _load_encoder(self, config: Dict[str, Any]) -> AbstractEncoder:
        """
        Modular encoder selection.
        Currently supports 'ffmpeg'; extend as needed.
        """
        engine = config.get("engine", "ffmpeg").lower()
        if engine == "ffmpeg":
            return FFmpegEncoder(config)
        else:
            raise ValueError(f"Unsupported encoder engine: {engine}")

    def _load_packager(self, config: Dict[str, Any]) -> AbstractPackager:
        """
        Modular packager selection.
        Supports 'bento4' or 'mp4box'.
        """
        engine = config.get("engine", "bento4").lower()
        if engine == "bento4":
            return Bento4Packager(config)
        elif engine == "mp4box":
            return MP4BoxPackager(config)
        else:
            raise ValueError(f"Unsupported packager engine: {engine}")

    def process(
        self,
        input_file: str,
        output_format: str = "mp4",
        dash_output_dir: Optional[str] = None,
    ) -> bool:
        """
        Main processing pipeline: encode/transcode, then optionally package to DASH.

        :param input_file: Source video file path.
        :param output_format: 'mp4' or 'ts'.
        :param dash_output_dir: Optional dir for DASH packaging.
        :return: True if successful.
        """
        output_file = input_file.rsplit(".", 1)[0] + f".{output_format}"
        temp_dir = "temp_segments"  # For intermediate files if needed

        with tqdm(total=100, desc="Processing video") as pbar:
            # Step 1: Encode/Transcode
            def progress_cb(pct):
                pbar.update(int(pct * 0.6))  # 60% for encoding

            if not self.encoder.encode(input_file, output_file, progress_cb):
                return False

            pbar.update(60)

            # Step 2: Optional DASH Packaging
            if dash_output_dir:
                os.makedirs(dash_output_dir, exist_ok=True)

                def pack_progress_cb(pct):
                    pbar.update(int(60 + pct * 0.4))  # 40% for packaging

                if not self.packager.package(
                    os.path.dirname(output_file), dash_output_dir, pack_progress_cb
                ):
                    return False

            pbar.update(40)
            pbar.close()

        print(f"Processing complete. Output: {output_file}")
        if dash_output_dir:
            print(f"DASH MPD: {dash_output_dir}/dash.mpd")
        return True
