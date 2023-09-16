'''
The domain-aware Data Access Layer for application logic.
'''
from datetime import date

from ..model import Event, Config, Exercise, SessionPlan
from .storage_backend import StorageBackend

class DAL:
    _backend: StorageBackend

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

    async def get_events(self, day: date = None) -> list[Event]:
        # TODO: Use query filter.
        events = await self._backend.query(Event)

        if day:
            day_events = list()
            for event in events:
                if event.when.date() == day:
                    day_events.append(event)
            return day_events
        
        return events
    
    async def get_exercises(self, type: str) -> list[Exercise]:
        return await self._backend.query(
            Exercise,
            filter={ 'type': type }
        )
    
    async def get_session_plans(self) -> list[SessionPlan]:
        return await self._backend.query(SessionPlan)

    # Mutations.
    async def create_event(self, event: Event):
        await self._backend.create(event)

    async def create_exercise(self, exercise: Exercise):
        await self._backend.create(exercise)

    async def create_session_plan(self, plan: SessionPlan):
        await self._backend.create(plan)

    async def update_session_plan(self, plan: SessionPlan):
        await self._backend.delete(
            SessionPlan, { 'name': plan.name }
        )
        await self._backend.create(plan)

    async def set_config(self, config: Config):
        await self._backend.delete(Config)
        await self._backend.create(config)

    # Computations.
    async def compute_exercise_totals(
        self, type: str, day: date = None
    ):
        exercises = await self.get_exercises(type)
        
        totals = dict()
        for exercise in exercises:
            events = await self._backend.query(
                Event,
                filter={
                    'type': type,
                    'exercise': exercise.name
                }
            )

            total = 0
            for event in events:
                # TODO: Use query filter.
                if day and event.when.date() != day:
                    continue

                total += event.value

            totals[exercise.name] = total

        return totals
