'''
Session plans are a preset series of exercises.
'''
from dataclasses import dataclass

from .model import Model
from .exercise import Exercise

@dataclass
class SessionPlan(Model):
    name: str = None
    exercises: list[Exercise] = None

    @classmethod
    def collection_name(cls) -> str:
        return 'session_plans'
