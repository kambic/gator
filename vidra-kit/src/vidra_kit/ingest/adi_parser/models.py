from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AppData:
    name: str
    value: str


@dataclass
class Asset:
    metadata: Dict[str, str]
    app_data: List[AppData] = field(default_factory=list)


@dataclass
class ADIMetadata:
    metadata: Dict[str, str]
    assets: List[Asset] = field(default_factory=list)
