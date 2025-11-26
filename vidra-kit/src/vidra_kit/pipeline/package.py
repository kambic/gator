import os

import ffmpeg
from celery import Celery

# from celery_config import app

from vidra_kit.ingest.celery_app import app


@app.task
def create_adaptive_package(vidra_payload):
    """
    @TODO: add documentation
    """
    print(f"extract_metadata msg is: {vidra_payload}")
    return {
        "ingest": {"done": True},
        "metadata": {"done": True},
        "package": {"done": True},
        "upload": {"done": False},
        "publish": {"done": False},
    }


@app.task
def transcode_video(input_path, output_dir, formats=["mp4", "webm"]):
    """
    Transcodes the input video into different formats.
    """
    for format in formats:
        output_path = os.path.join(
            output_dir, f"{os.path.splitext(os.path.basename(input_path))[0]}.{format}"
        )
        print(f"Transcoding video to {output_path}")

        # Use ffmpeg to transcode
        ffmpeg.input(input_path).output(output_path).run()

    return f"Transcoding complete, files saved to {output_dir}"


@app.task
def package_hls(input_path, output_dir):
    """
    Packages the input video into HLS format.
    """
    output_hls = os.path.join(output_dir, "hls")
    os.makedirs(output_hls, exist_ok=True)

    # FFmpeg HLS packaging command
    print(f"Packaging video {input_path} into HLS...")
    ffmpeg.input(input_path).output(
        f"{output_hls}/output.m3u8", format="hls", hls_time=10, hls_list_size=0
    ).run()

    return f"HLS packaging complete. Files stored in {output_hls}"


@app.task
def package_dash(input_path, output_dir):
    """
    Packages the input video into DASH format.
    """
    output_dash = os.path.join(output_dir, "dash")
    os.makedirs(output_dash, exist_ok=True)

    # FFmpeg DASH packaging command
    print(f"Packaging video {input_path} into DASH...")
    ffmpeg.input(input_path).output(f"{output_dash}/output.mpd", format="dash").run()

    return f"DASH packaging complete. Files stored in {output_dash}"


@app.task
def simple():
    from ffmpeg_streaming import Formats, Representation, Size, Bitrate
    from ffmpeg_streaming import FFmpeg

    # Input video file
    video = FFmpeg("input.mp4")

    # Output directory for HLS segments
    hls_output = "vod_output/hls"

    _240p = Representation(Size(426, 240), Bitrate(200_000, 400_000))
    _360p = Representation(Size(640, 360), Bitrate(400_000, 800_000))
    _480p = Representation(Size(854, 480), Bitrate(800_000, 1_200_000))
    _720p = Representation(Size(1280, 720), Bitrate(1_200_000, 2_500_000))
    _1080p = Representation(Size(1920, 1080), Bitrate(3_000_000, 5_000_000))

    video.hls(Formats.h264()).auto_generate_representations().output(hls_output)

    dash_output = "vod_output/dash"

    video.dash(Formats.h264()).auto_generate_representations().output(dash_output)
