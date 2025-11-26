import logging
from rich.logging import RichHandler

# Configure rich logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("vidra_kit")

logger.debug("Init by: %s %s" % (__name__, __file__))


def ff_out():
    return


from dataclasses import dataclass, field
from pathlib import Path
import uuid


@dataclass
class TestSample:
    input_path: Path  # Path to input file or data
    output_dir: Path  # Unique path to output folder

    def __post_init__(self):
        # Ensure output_dir is a simple unique path by appending a UUID if not already unique
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            unique_suffix = str(uuid.uuid4())[:8]  # Short UUID for simplicity
            self.output_dir = (
                self.output_dir.parent / f"{self.output_dir.name}_{unique_suffix}"
            )
            self.output_dir.mkdir(parents=True, exist_ok=True)


input_sample = "/home/kamba/neo/vidra_kit/media/src/samples/TearsOfSteel.mp4"


@dataclass
class IOConfig:
    input: str = input_sample  # Default input path
    output: Path = field(default_factory=lambda: IOConfig.generate_unique_output_path())

    @staticmethod
    def generate_unique_output_path(root: Path = Path("./media/outputs")) -> Path:
        unique_id = uuid.uuid4().hex[:8]  # short unique id
        path = root / f"run_{unique_id}"
        path.mkdir(parents=True, exist_ok=True)
        return path


__all__ = ["logger", "IOConfig"]
