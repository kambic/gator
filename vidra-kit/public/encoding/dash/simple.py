import ffmpeg

input_file = "media/src/bbb/bbb_sunflower_1080p_60fps_normal.mp4"
output_dir = "media/out/dash/simple"
output_manifest = f"{output_dir}/stream.mpd"

# Ensure output dir exists
import os

os.makedirs(output_dir, exist_ok=True)

if False:
    ffmpeg.input("input.mp4").output(
        "processed.mp4", vcodec="libx264", acodec="aac", strict="experimental"
    ).run()
print(__name__)
# Create ffmpeg command

ff_input = ffmpeg.input(input_file)

ff_out = ff_input.output(
    output_manifest,
    format="dash",  # MPEG-DASH container
    map="0",  # Map all streams
    use_timeline=1,
    use_template=1,
    init_seg_name="init-$RepresentationID$.mp4",
    media_seg_name="chunk-$RepresentationID$-$Number$.m4s",
    remove_at_exit=1,  # Keep temp files
    adaptation_sets="id=0,streams=v id=1,streams=a",
).run(overwrite_output=True)
