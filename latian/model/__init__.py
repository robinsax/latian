'''
Application data model.
'''
from typing import Type

from .model import Model
from .event import Event
from .config import Config, create_default_config
from .session_plan import SessionPlan
from .exercise import EXERCISE_TYPES, Exercise, create_default_exercises

def get_schema() -> dict[str, Type[Model]]:
    schema = dict()
    for Type in (Event, Config, Exercise, SessionPlan):
        schema[Type.collection_name()] = Type

    return schema
