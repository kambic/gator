"""
Video Processor Package
A modular Python package for video encoding, transcoding (MP4/TS), and DASH packaging.
Supports FFmpeg for encoding and Bento4/MP4Box for packaging.
"""

from .video_processor import VideoProcessor
from .encoders import FFmpegEncoder
from .packagers import Bento4Packager, MP4BoxPackager

__version__ = "0.1.1"
__all__ = ["VideoProcessor", "FFmpegEncoder", "Bento4Packager", "MP4BoxPackager"]
