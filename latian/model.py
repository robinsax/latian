from datetime import datetime
from dataclasses import dataclass, asdict, fields

class Model:

    @classmethod
    def attributes(cls):
        return fields(cls)

    @classmethod
    def from_dict(cls, model_dict: dict) -> 'Model':
        return cls(**model_dict)
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class Config(Model):
    exit_message: str = 'cya'
    milestone_reps: int = 100
    milestone_seconds: int = 18000
    timer_delay_seconds: int = 5
    loaded: bool = False

@dataclass
class Event(Model):
    mode: str = None
    exercise: str = None
    value: int = None
    when: datetime = None

    @property
    def is_rep(self):
        return self.mode == 'rep'

    def is_milestone(self, prev_total: int, config: Config) -> bool:
        milestone = 0
        if self.is_rep:
            milestone = config.milestone_reps
        else:
            milestone = config.milestone_seconds

        return int(prev_total/milestone) < int((prev_total + self.value)/milestone)
