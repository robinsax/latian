from typing import Any

from ..model import Event, Config
from .backend import StorageBackend, storage_backends

from . import file_system

class DAL:
    _backend: StorageBackend = None
    _events: list[Event] = None
    _config: Config = None
    _exercises: dict[list] = None

    def __init__(self, backend: StorageBackend):
        self._backend = backend
        self._events = list()
        self._config = None
        self._exercises = dict()

    @property
    def events(self):
        return self._events

    @property
    def config(self):
        return self._config
    
    def get_exercises(self, mode: str) -> list[str]:
        return self._exercises[mode]

    def connect(self):
        self._backend.connect()

        for event_dict in self._backend.get_events():
            self._events.append(Event.from_dict(event_dict))

        self._exercises = self._backend.get_exercises()
        self._config = Config.from_dict(self._backend.get_config())

    def commit(self):
        self._backend.commit()

    def push_event(self, event: Event):
        self._events.append(event)
        self._backend.push_event(event.to_dict())

    def push_exercise(self, mode: str, exercise: str):
        self._exercises[mode].append(exercise)
        self._backend.push_exercise(mode, exercise)

    def update_config(self, key: str, value: Any):
        setattr(self._config, key, value)
        self._backend.set_config(self._config.to_dict())

    def compute_event_totals(self, mode: str):
        totals = { key: 0 for key in self.get_exercises(mode) }

        for event in self.events:
            if event.mode != mode:
                continue

            totals[event.exercise] += event.value
        
        return totals
