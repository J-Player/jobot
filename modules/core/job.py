from dataclasses import dataclass


@dataclass
class Job:
    id: str
    url: str = None
    title: str = None
    description: str = None
    location: str = None
    company: str = None
