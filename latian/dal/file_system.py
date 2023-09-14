import json
import os.path
from typing import Any
from datetime import datetime

from .backend import StorageBackend, storage_backends

DATETIME_FORMAT = '%d/%m/%Y %H:%M'

@storage_backends.implementation('file')
class FileSystemStorageBackend(StorageBackend):
    file_path: str = None
    events: list[dict] = list()
    config: dict[Any] = dict()
    exercises: dict[list[str]] = dict()

    def __init__(self, target_str: str):
        self.file_path = target_str

    def connect(self) -> bool:
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
        return self.exercises

    def push_event(self, event: dict):
        self.events.append(event)

    def push_exercise(self, mode: str, exercise: str):
        self.exercises[mode].append(exercise)

    def set_config(self, config: dict):
        self.config = config
