# vidra-kit

A modular Python package for video encoding, transcoding (MP4/TS), and DASH packaging.

## Features

- Video encoding with `av`, `moviepy`, `imageio-ffmpeg`
- Asynchronous task support with Celery
- CLI tools for video processing and thumbnail generation
- Easy integration with Django projects like `alligator`

## Installation

### Requirements

- Python 3.8+
- FFmpeg installed and available in PATH

### Installation

Install via PyPI (production):

```bash
pip install vidra-kit
````

Or install locally for development:

```bash
git clone <vidra-kit-repo-url>
cd vidra-kit
pip install -e .
```

Or via `uv`:

```bash
uv sync --dev
```

## Usage

### CLI

```bash
vidra-kit --help
vidra-ping
vidra-thumbs
```

### API

Import and use modules in your Python code:

```python
from vidra_kit import cli
```

---

## Development

* Uses `uv` build backend for packaging and publishing
* Run tests with:

```bash
pytest
```

* Publish package:

```bash
uv build
uv publish
```

---

## Contributing

Feel free to open issues or PRs.

---

## License

MIT (or specify your license here)

---

# Contact

[rok.kambic@mx.si](mailto:rok.kambic@mx.si)