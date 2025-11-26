import argparse
import sys
from .video_processor import VideoProcessor
from .encoders.ffmpeg_encoder import FFmpegEncoder
from .packagers.bento4_packager import Bento4Packager
from .packagers.mp4box_packager import MP4BoxPackager


def cli():
    parser = argparse.ArgumentParser(
        prog="video-tool",
        description="Video transcoding and packaging CLI using FFmpeg and Bento4/MP4Box.",
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Path to input video file."
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Path to output video file."
    )
    parser.add_argument(
        "--encoder",
        choices=["ffmpeg"],
        default="ffmpeg",
        help="Encoder to use (currently only 'ffmpeg').",
    )
    parser.add_argument(
        "--packager",
        choices=["bento4", "mp4box", "none"],
        default="none",
        help="Optional packager to use.",
    )
    parser.add_argument(
        "--bitrate",
        help="Target video bitrate (e.g. 2500k).",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show encoding progress percentage in console.",
    )

    return parser.parse_args()


def maiold():
    args = cli()

    # --- Encoder setup ---
    if args.encoder == "ffmpeg":
        config = {}
        if args.bitrate:
            config["video_bitrate"] = args.bitrate
        encoder = FFmpegEncoder(config=config)
    else:
        print(f"Unsupported encoder: {args.encoder}")
        sys.exit(1)

    # --- Optional progress callback ---
    def progress_cb(p: float):
        print(f"\rProgress: {p*100:.1f}%", end="", flush=True)

    print(f"Encoding: {args.input} → {args.output}")
    ok = encoder.encode(
        args.input,
        args.output,
        progress_cb if args.progress else None,
    )

    if not ok:
        print("\n❌ Encoding failed.")
        sys.exit(1)

    print("\n✅ Encoding complete.")

    # --- Packaging (optional) ---
    if args.packager != "none":
        print(f"Packaging using {args.packager}...")
        if args.packager == "bento4":
            packager = Bento4Packager()
        elif args.packager == "mp4box":
            packager = MP4BoxPackager()
        else:
            print("Unknown packager, skipping.")
            return

        success = packager.package(args.output)
        print("✅ Packaging complete." if success else "❌ Packaging failed.")


def main():
    args = cli()

    encoder_cfg = {"engine": args.encoder}
    if args.bitrate:
        encoder_cfg["video_bitrate"] = args.bitrate

    packager_cfg = {"engine": args.packager}

    processor = VideoProcessor(encoder_cfg, packager_cfg)
    processor.process(
        args.input, args.output.split(".")[-1], dash_output_dir="output_dash"
    )


if __name__ == "__main__":
    main()
