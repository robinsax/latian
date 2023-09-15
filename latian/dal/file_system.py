import json
import os.path
from typing import Any
from datetime import datetime

from ..common import MODES
from .backend import StorageBackend, storage_backends

DATETIME_FORMAT = '%d/%m/%Y %H:%M'

@storage_backends.implementation('file')
class FileSystemStorageBackend(StorageBackend):
    file_path: str = None
    events: list[dict] = None
    config: dict[Any] = None
    exercises: dict[list[str]] = None

    def __init__(self, cli_args):
        super().__init__(cli_args)
        self.file_path = None
        self.events = list()
        self.config = dict()
        self.exercises = { key: list() for key in MODES }

    def connect(self) -> bool:
        self.file_path = self.cli_args.get('storage_dest')
        if not os.path.isfile(self.file_path):
            return

        with open(self.file_path, 'r') as dal_io:
            data = json.load(dal_io)

            self.config = data['config']
            self.exercises = data['exercises']

            self.events = data['events']
            for event in self.events:
                event['when'] = datetime.strptime(event['when'], DATETIME_FORMAT)

    def commit(self):
        safe_events = list()
        for event in self.events:
            safe_events.append({
                **event,
                'when': event['when'].strftime(DATETIME_FORMAT)
            })

        with open(self.file_path, 'w') as dal_io:
            json.dump({
                'events': safe_events,
                'exercises': self.exercises,
                'config': self.config
            }, dal_io)

    def get_events(self) -> list[dict]:
        return self.events
    
    def get_config(self) -> dict[Any]:
        return self.config
    
    def get_exercises(self) -> dict[list[str]]:
        return {
            key: list(self.exercises[key]) for key in self.exercises
        }

    def push_event(self, event: dict):
        self.events.append(event)

    def push_exercise(self, mode: str, exercise: str):
        self.exercises[mode].append(exercise)

    def set_config(self, config: dict):
        self.config = config
