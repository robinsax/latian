from typing import Any

from ..common import ImplementationRegistry

storage_backends = ImplementationRegistry()

class StorageBackend:
    '''Persistant storage for domain objects.'''

    def __init__(self, target_str: str):
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def get_events(self) -> list[dict]:
        raise NotImplementedError()
    
    def get_config(self) -> dict[Any]:
        raise NotImplementedError()
    
    def get_exercises(self) -> dict[list[str]]:
        raise NotImplementedError()

    def push_event(self, event: dict):
        raise NotImplementedError()
    
    def push_exercise(self, mode: str, exercise: str):
        raise NotImplementedError()

    def set_config(self, config: dict):
        raise NotImplementedError()
