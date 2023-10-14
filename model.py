from dataclasses import dataclass
from datetime import datetime


@dataclass
class Weather:
    time: datetime
    city: str
    temperature: float
    feels_like: float
    description: str
    wind: float
