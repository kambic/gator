from abc import ABC, abstractmethod
from typing import Dict, Any, List
import subprocess


class AbstractPackager(ABC):
    """
    Abstract base class for DASH packagers.
    Subclasses must implement the package method.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def package(
        self, input_dir: str, output_dir: str, progress_callback: callable = None
    ) -> bool:
        """
        Packages the input files (MP4/TS) into DASH segments.

        :param input_dir: Directory containing input MP4/TS files.
        :param output_dir: Directory for DASH output (MPD and segments).
        :param progress_callback: Optional callback for progress updates.
        :return: True if successful, False otherwise.
        """
        pass

    def _run_command(self, cmd: List[str], progress_callback: callable = None) -> bool:  # type: ignore
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
                progress_callback(100)
            return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
