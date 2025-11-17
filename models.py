# models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: int
    text: str
    completed: bool
    priority: str  # 'low', 'normal', 'high'
    created_at: str  # ISO format
    alarm_time: str = None  # ISO format or None

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row[0],
            text=row[1],
            completed=bool(row[2]),
            priority=row[3],
            created_at=row[4],
            alarm_time=row[5]
        )