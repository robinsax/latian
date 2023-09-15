from random import randint
from datetime import datetime

from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Event, Exercise
from . import actions

@actions.implementation('start session')
async def session_action(dal: DAL, io: IO):
    config = await dal.get_config()

    while True:
        type = await io.read_choice((*EXERCISE_TYPES, 'random'), 'mode')
        is_random = type == 'random'
        if is_random:
            type = EXERCISE_TYPES[randint(0, 1)]

        exercises = await dal.get_exercises(type)
        if not len(exercises):
            await io.read_signal('add exercises first')
            return

        name: str = None
        if is_random:
            name = exercises[randint(0, len(exercises) - 1)].name

            title = '%s (%s)'%(name, type)
            if await io.read_choice(('yes', 'no'), title) == 'no':
                continue
        else:
            names = list(
                exercise.name for exercise in exercises
            )
            name = await io.read_choice(names, 'which')

        event = Event(
            type=type,
            exercise=name,
            value=0,
            when=datetime.now()
        )
        if event.is_rep:
            event.value = await io.read_int('how many?', min=1)
        else:
            start = datetime.now()

            with io.timer(config.timer_delay_seconds):
                await io.read_signal()
            event.value = (
                (datetime.now() - start).seconds -
                config.timer_delay_seconds
            )
            if event.value < 0:
                continue

        io.write_event(event, prefix='+')
        await dal.create_event(event)
        await dal.commit()
