from dataclasses import dataclass
from datetime import datetime

@dataclass
class IndeedJob:
    id: str
    url: str
    title: str
    rating: float
    description: str
    easy_application: bool
    location: str
    company: str
    salary: str
    job_types: list[str]
    work_shifts: list[str]