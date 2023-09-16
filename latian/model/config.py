'''
Per-user configuration.
'''
from dataclasses import dataclass

from .model import Model

@dataclass
class Config(Model):
    exit_message: str = None
    milestone_reps: int = 0
    milestone_seconds: int = 0
    timer_delay_seconds: int = 0
    loaded: bool = False

    @classmethod
    def collection_name(cls) -> str:
        return 'config'

def create_default_config():
    return Config(
        exit_message='cya',
        milestone_reps=100,
        milestone_seconds=300,
        timer_delay_seconds=5,
        loaded=False
    )
