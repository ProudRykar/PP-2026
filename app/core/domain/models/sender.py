from dataclasses import dataclass
from typing import Dict, Any


@dataclass(slots=True)
class Sender:
    id: str
    apps: Dict[str, Any]
