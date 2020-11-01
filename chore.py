from dataclasses import dataclass

@dataclass
class Chore:
    chore_id: str
    name: str
    email: str
    start_date: str
    chore_type: str
    chore_text: str
    chore_duration: int
    overdue: bool
