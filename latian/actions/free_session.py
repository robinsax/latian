from random import randint
from datetime import datetime

from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Event, Exercise
from .common import run_exercise
from . import actions

@actions.implementation('start free session')
async def free_session_action(dal: DAL, io: IO):
    config = await dal.get_config()

    while True:
        type = await io.read_choice(
            (*EXERCISE_TYPES, 'random'),
            'exercise type'
        )
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
            name = await io.read_choice((*names, 'back'), 'which')
            if name == 'back':
                continue

        await run_exercise(
            io, dal, config,
            Exercise(
                type=type,
                name=name
            )
        )
