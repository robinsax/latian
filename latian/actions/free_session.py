from random import randint
from datetime import datetime

from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise
from .common import run_exercise
from . import actions

@actions.implementation('start free session')
async def free_session_action(dal: DAL, io: IO):
    config = await dal.get_config()

    with io.temporary_write() as session_out:
        while True:
            type = await io.read_choice(
                (*EXERCISE_TYPES, 'random'), 'exercise type',
                control_options=('done',)
            )
            if type == 'done':
                with io.temporary_write() as confirm_out:
                    confirm_out.write_message(config.exit_message)

                    if await io.read_confirm('are you sure?'):
                        return
                    else:
                        continue

            is_random = type == 'random'
            if is_random:
                index = randint(0, len(EXERCISE_TYPES) - 1)
                type = EXERCISE_TYPES[index]

            exercises = await dal.get_exercises(type)
            if not len(exercises):
                await io.read_signal('add exercises first')
                return

            name: str = None
            if is_random:
                exercise = exercises[randint(0, len(exercises) - 1)]

                with io.temporary_write() as confirm_out:
                    confirm_out.write_exercise(exercise)
                    if not await io.read_confirm('this?'):
                        continue

                name = exercise.name
            else:
                name = await io.read_choice(
                    (exercise.name for exercise in exercises),
                    'which',
                    control_options=('back',)
                )
                if name == 'back':
                    continue

            await run_exercise(
                io, session_out, dal, config,
                Exercise(
                    type=type,
                    name=name
                )
            )
