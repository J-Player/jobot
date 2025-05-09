from dataclasses import dataclass
from typing import Any

from modules.core import Job


@dataclass
class IndeedJob(Job):
    benefits: str = None
    easy_application: bool = None
    details: dict[str, Any] = None
