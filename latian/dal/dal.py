'''
The domain-aware Data Access Layer for application logic.
'''
from typing import Any

from ..model import Event, Config, Exercise
from .storage_backend import StorageBackend, Aggregation

class DAL:
    _backend: StorageBackend = None

    def __init__(self, backend: StorageBackend):
        self._backend = backend

    async def connect(self, user: str):
        await self._backend.connect(user)

    async def disconnect(self):
        await self._backend.disconnect()

    async def commit(self):
        await self._backend.commit()

    # Getters.
    async def get_config(self) -> Config:
        configs = await self._backend.query(Config)
        if not len(configs):
            return None
        
        return configs[0]

    async def get_events(self) -> list[Event]:
        return await self._backend.query(Event)
    
    async def get_exercises(self, type: str) -> list[Exercise]:
        return await self._backend.query(
            Exercise,
            filter={ 'type': type }
        )

    # Mutations.
    async def create_event(self, event: Event):
        await self._backend.create(event)

    async def create_exercise(self, exercise: Exercise):
        await self._backend.create(exercise)

    async def set_config(self, config: Config):
        await self._backend.delete(Config)
        await self._backend.create(config)

    # Computations.
    async def compute_exercise_totals(self, type: str):
        exercises = await self.get_exercises(type)
        
        totals = dict()
        for exercise in exercises:
            totals[exercise.name] = await self._backend.query(
                Event,
                filter={
                    'type': type,
                    'exercise': exercise.name
                },
                aggregation=(Aggregation.sum, 'value')
            )

        return totals
