**main**.py (CLI entrypoint)
│
└──▶ cli() → main()
│
├──▶ Parse CLI args (input, output, encoder, packager, bitrate, etc.)
│
├──▶ Instantiate FFmpegEncoder(config)
│
├──▶ encoder.encode(input, output, progress_cb)
│ │
│ ├──▶ \_get_duration(input)
│ │ └──▶ ffprobe (to get duration)
│ │
│ ├──▶ ffmpeg subprocess
│ │ └──▶ Read stderr for time= markers
│ │ └──▶ progress_callback(progress)
│ │
│ └──▶ Return success/failure (bool)
│
├──▶ If packager != none:
│ │
│ ├──▶ Bento4Packager.package(output)
│ │ or
│ └──▶ MP4BoxPackager.package(output)
│
└──▶ Print result, exit with status code
`--output output.mp4 --encoder ffmpeg --packager bento4`
`python -m vidra_kit.video -i int.mp4 --output output.mp4 --encoder ffmpeg --packager bento4`
