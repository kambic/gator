import subprocess
import tempfile
from pathlib import Path


def test_cli_generate(tmp_path):
    input_path = tmp_path / "input.yaml"
    output_path = tmp_path / "output.xml"
    input_path.write_text(
        """
title:
  en: "Test CLI"
asset_id: "CLI123"
poster_id: "CLI123-POSTER"
poster_resolution: "1280x720"
movie_bitrate: "9000000"
default_lang: "en"
"""
    )
    result = subprocess.run(
        [
            "python",
            "-m",
            "adi_toolkit.cli",
            "generate",
            str(input_path),
            str(output_path),
        ]
    )
    assert output_path.exists()
