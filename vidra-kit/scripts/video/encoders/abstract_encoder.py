from abc import ABC, abstractmethod
from typing import List, Dict, Any
import subprocess


class AbstractEncoder(ABC):
    """
    Abstract base class for video encoders.
    Subclasses must implement the encode method.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def encode(
        self, input_file: str, output_file: str, progress_callback: callable = None
    ) -> bool:
        """
        Encodes/transcodes the input file to the output file.

        :param input_file: Path to source video file.
        :param output_file: Path to output file (e.g., .mp4 or .ts).
        :param progress_callback: Optional callback for progress updates (e.g., percentage).
        :return: True if successful, False otherwise.
        """
        pass

    def _run_command(self, cmd: List[str], progress_callback: callable = None) -> bool:
        """
        Helper to run subprocess commands with progress if supported.
        """
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Error: {stderr}")
                return False
            if progress_callback:
                progress_callback(100)  # Simple completion callback
            return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
