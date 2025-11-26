## 📘 Ingest

Transcoding & Encoding:

- **Transcoding & Encoding** (HLS/DASH)
- **Packaging**

---

## Transcoding & Encoding:

Convert source files into multiple delivery formats and bitrates for adaptive streaming (HLS, DASH).
Codecs: H.264, H.265 (HEVC), AV1.
Tools: FFmpeg, Elemental, AWS MediaConvert, Telestream.

---

## Packaging:

Bundle media with metadata and assets (thumbnails, captions, alternate audio, subtitles).
DRM and encryption can be added at this stage (Widevine, FairPlay, PlayReady).

---

## Content Delivery:

Upload to Content Delivery Servers (EW), storage for playback via OTT platforms, apps, or websites.
Includes publishing to CMS with proper versioning, scheduling, and geo-blocking settings.

---

## 🧪 Example Commands

### Adaptive Streaming (HLS)

```bash
ffmpeg -i input.mp4 -preset fast -g 48 -sc_threshold 0 \
-map 0:v -map 0:a -s:v:0 1920x1080 -b:v:0 5000k \
-map 0:v -map 0:a -s:v:1 1280x720 -b:v:1 2800k \
-map 0:v -map 0:a -s:v:2 854x480 -b:v:2 1400k \
-f hls -hls_time 4 -hls_playlist_type vod \
-master_pl_name master.m3u8 \
-var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2" \
hls/output_%v.m3u8
```

### RTSP Stream

```bash
ffmpeg -re -i input.mp4 -c copy -f rtsp rtsp://localhost:8554/stream
```

---

## 🧵 Workflow Summary

1. **Ingest Source Files**
2. **Transcode to Multiple Renditions**
3. **Package Streams**
4. **Generate Manifests (HLS/DASH)**
5. **Prepare RTSP-compatible Stream**
6. **Store and Deliver via CDN or RTSP Server**

## 📁 Files

```
vod_pipeline/
│
├── vod_pipeline/ # Main package
│ ├── **init**.py
│ ├── config.py # Settings loader (envvars, .env, etc.)
│ ├── celery_app.py # Celery app config
│ ├── tasks/ # Celery task modules
│ │ ├── **init**.py
│ │ ├── ingest.py # Ingest raw files (pull/push/transcode)
│ │ ├── metadata.py # Extract/transform metadata
│ │ ├── publish.py # Publish to CMS (via API)
│ │ ├── package.py # Create HLS/DASH adaptive packages
│ │ └── upload.py # Upload to CDN/streaming host
│ ├── services/ # Integration clients
│ │ ├── **init**.py
│ │ ├── cms_client.py # REST API client for CMS
│ │ ├── transcoder.py # Local or remote transcoder wrapper (FFmpeg or API)
│ │ ├── storage.py # S3, GCS, FTP clients, etc.
│ │ └── notifier.py # Slack/email/HTTP callbacks, etc.
│ ├── workflows/ # Task chaining logic
│ │ ├── **init**.py
│ │ └── vod_ingest_flow.py # Orchestration of the entire VOD pipeline
│ └── utils/ # Common helpers, e.g. path utils, logging, etc.
│ ├── **init**.py
│ └── logger.py
│
├── tests/ # Unit and integration tests
│ ├── conftest.py
│ ├── tasks/
│ ├── services/
│ └── workflows/
│
├── docker/ # Optional Docker setup
│ ├── Dockerfile
│ └── celery_worker.sh
│
├── .env # Environment variables (never commit)
├── requirements.txt # Prod deps
├── requirements-dev.txt # Dev/test deps
├── celeryconfig.py # Optional: Celery config if not using env/config.py
├── cli.py # Entrypoint for CLI / management
├── README.md
└── pyproject.toml / setup.py # Packaging metadata
```

## 🔧 Technologies Used for Transcoding & Packaging

| Tool                   | Purpose          |
| ---------------------- | ---------------- |
| Celery                 | Tasks processing |
| RabbitMQ               | broker/queues    |
| FFmpeg                 | transcoding      |
| Shaka Packager         | packaging        |
| CMS API                | REST/GraphQL     |
| FTP/SMB                | Isilon Storage   |
| Pydantic / Marshmallow | Isilon Storage   |
| Typer                  | CLI entrypoints  |
| pytest                 | Tests            |

---

## 📦 Usage

Usage

# Run full ingest flow

python manage.py run-workflow "s3://vod-bucket/video123.mov"

# Start worker

python manage.py worker

# Start beat (if using periodic tasks)

python manage.py beat

# Check worker status

python manage.py status

# Retry a task (placeholder logic)

## python manage.py replay <task_id>

✅ Requirements

🔄 Future Extensions

    schedule-workflow – queue up tasks for later using eta or beat.

    inspect-queue – show pending tasks.

    clear-stuck-tasks – cleanup helper.

    generate-report – export VOD job logs/metadata.

Example Usage

# Run full chain

python manage.py run-workflow "s3://bucket/asset.mov"

# Run individual tasks

python manage.py task ingest "s3://bucket/asset.mov"
python manage.py task metadata "/tmp/asset.mp4"
python manage.py task package "/tmp/asset.mp4"
python manage.py task upload "/tmp/output/hls/"
python manage.py task publish "/tmp/metadata.json"

# Start worker

python manage.py worker

# Check status

python manage.py status
