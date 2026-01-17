from dataclasses import dataclass, asdict
from typing import Any, Optional

@dataclass
class Response:
    success: bool
    code: Optional[str] = None
    data: Optional[Any] = None
    details: Optional[dict] = None

    def to_dict(self):
        return asdict(self)