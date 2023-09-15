'''
Exercises.
'''
from dataclasses import dataclass

from .model import Model

EXERCISE_TYPES = ('rep', 'timed')

@dataclass
class Exercise(Model):
    type: str = None
    name: str = None

    @classmethod
    def collection_name(cls) -> str:
        return 'exercises'

    @property
    def is_rep(self):
        return self.type == 'rep'

def create_default_exercises() -> tuple[Exercise]:
    return (
        Exercise(type='rep', name='push up'),
        Exercise(type='rep', name='sit up'),
        Exercise(type='timed', name='plank')
    )
