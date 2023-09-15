from random import randint
from datetime import datetime

from ..io import IO
from ..dal import DAL, Event
from ..common import MODES
from . import actions

@actions.implementation('start session')
async def session_action(dal: DAL, io: IO):
    while True:
        mode = await io.read_selection((*MODES, 'random'), 'mode')
        is_random = mode == 'random'
        if is_random:
            mode = MODES[randint(0, 1)]

        exercises = dal.get_exercises(mode)
        if not len(exercises):
            await io.read_signal('add exercises first')
            return

        exercise: str = None
        if is_random:
            exercise = exercises[randint(0, len(exercises) - 1)]

            title = '%s (%s)'%(exercise, mode)
            if await io.read_selection(('yes', 'no'), title) == 'no':
                continue
        else:
            exercise = await io.read_selection(exercises, 'which')

        event = Event(
            mode=mode,
            exercise=exercise,
            value=0,
            when=datetime.now()
        )
        if event.is_rep:
            event.value = await io.read_int('how many?', min=1)
        else:
            delay = dal.config.timer_delay_seconds
            start = datetime.now()

            with io.timer(delay):
                await io.read_signal()

            event.value = (datetime.now() - start).seconds - delay
            if event.value < 0:
                continue

        io.write_event(event, prefix='+')
        dal.push_event(event)
        dal.commit()
