from pathlib import Path
from typing import List, Tuple, Optional
import ffmpeg


class DashTranscoder:
    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        use_opus: bool = False,
        subtitle_file: Optional[Path] = None,
    ):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.use_opus = use_opus
        self.subtitle_file = subtitle_file

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video renditions: (height, video_bitrate, audio_bitrate)
        self.renditions: List[Tuple[int, str, str]] = [
            (1080, "5000k", "192k"),
            (720, "3000k", "128k"),
            (480, "1500k", "96k"),
        ]

    def transcode_representations(self) -> List[Path]:
        transcoded_files = []

        for height, v_bitrate, _ in self.renditions:
            out_file = self.output_dir / f"video_{height}p.mp4"

            print(f"▶ Transcoding {height}p @ {v_bitrate}...")
            (
                ffmpeg.input(str(self.input_file))
                .filter("scale", -2, height)
                .output(
                    str(out_file),
                    vcodec="libx264",
                    video_bitrate=v_bitrate,
                    preset="fast",
                    crf=20,
                    an=None,  # Remove audio
                )
                .overwrite_output()
                .run()
            )

            transcoded_files.append(out_file)

        return transcoded_files

    def extract_audio(self) -> Path:
        ext = "opus" if self.use_opus else "mp4"
        audio_file = self.output_dir / f"audio.{ext}"

        codec = "libopus" if self.use_opus else "aac"
        print(f"🎧 Extracting audio using {codec} codec...")

        output_args = {"acodec": codec, "audio_bitrate": "128k", "vn": None}  # No video

        (
            ffmpeg.input(str(self.input_file))
            .output(str(audio_file), **output_args)
            .overwrite_output()
            .run()
        )

        return audio_file

    def convert_subtitles(self) -> Optional[Path]:
        """
        Convert SRT/ASS to WebVTT if needed (Shaka prefers VTT)
        """
        if not self.subtitle_file:
            return None

        subtitle_ext = self.subtitle_file.suffix.lower()
        output_sub = self.output_dir / "subs.vtt"

        if subtitle_ext == ".vtt":
            print("📝 Using VTT subtitles directly.")
            return self.subtitle_file

        print(f"📝 Converting subtitles {self.subtitle_file.name} → VTT...")
        (
            ffmpeg.input(str(self.subtitle_file))
            .output(str(output_sub), format="webvtt")
            .overwrite_output()
            .run()
        )

        return output_sub

    def package_dash(
        self,
        video_files: List[Path],
        audio_file: Path,
        subtitle_file: Optional[Path],
        output_mpd: str = "stream.mpd",
    ):
        print("📦 Packaging into MPEG-DASH...")

        input_streams = []
        map_args = []
        video_ids = []

        # Add video tracks
        for i, video_file in enumerate(video_files):
            input_streams.append(ffmpeg.input(str(video_file)))
            map_args += [("-map", f"{i}:v:0")]
            video_ids.append(str(i))

        # Add audio track
        input_streams.append(ffmpeg.input(str(audio_file)))
        audio_index = len(video_files)
        map_args += [("-map", f"{audio_index}:a:0")]

        # Add subtitles (if provided)
        subtitle_index = None
        if subtitle_file:
            input_streams.append(ffmpeg.input(str(subtitle_file)))
            subtitle_index = len(video_files) + 1
            map_args += [("-map", f"{subtitle_index}:s:0")]

        adaptation_sets = [
            f"id=0,streams={','.join(video_ids)}",
            f"id=1,streams={audio_index}",
        ]

        if subtitle_index is not None:
            adaptation_sets.append(f"id=2,streams={subtitle_index},roles=subtitles")

        output_path = self.output_dir / output_mpd

        (
            ffmpeg.output(
                *input_streams,
                str(output_path),
                format="dash",
                use_template=1,
                use_timeline=1,
                init_seg_name="init-$RepresentationID$.mp4",
                media_seg_name="chunk-$RepresentationID$-$Number$.m4s",
                adaptation_sets=" ".join(adaptation_sets),
                **dict(map_args),
            )
            .overwrite_output()
            .run()
        )

        print(f"✅ DASH manifest ready: {output_path.name}")

    def run(self):
        print(f"🎬 Processing {self.input_file.name}")

        video_files = self.transcode_representations()
        audio_file = self.extract_audio()
        subtitle = self.convert_subtitles()
        self.package_dash(video_files, audio_file, subtitle)


if __name__ == "__main__":
    from pathlib import Path

    transcoder = DashTranscoder(
        input_file=Path("media/src/bbb/bbb_sunflower_1080p_60fps_normal.mp4"),
        output_dir=Path("media/out/dash/modern"),
        use_opus=True,
        # subtitle_file=Path("subtitles.srt"),  # Can also use .vtt
    )
    transcoder.run()
