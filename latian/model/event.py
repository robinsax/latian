'''
Events of exercises being performed.
'''
from datetime import datetime
from dataclasses import dataclass

from .model import Model
from .config import Config

@dataclass
class Event(Model):
    type: str = None
    exercise: str = None
    value: int = None
    when: datetime = None

    @classmethod
    def collection_name(cls) -> str:
        return 'events'

    @property
    def is_rep(self):
        return self.type == 'rep'

    def is_milestone(self, prev_total: int, config: Config) -> bool:
        milestone = 0
        if self.is_rep:
            milestone = config.milestone_reps
        else:
            milestone = config.milestone_seconds

        return int(prev_total/milestone) < int((prev_total + self.value)/milestone)
