from random import randint
from datetime import datetime

from ..io import IO
from ..dal import DAL, Event
from ..common import MODES
from . import actions

@actions.implementation('session')
def session_action(dal: DAL, io: IO):
    while True:
        mode = io.read_selection((*MODES, 'random'), 'mode')

        exercises: list[str] = list()
        rand_mode: str = None
        if mode == 'random':
            rand_mode = MODES[randint(0, 1)]
            exercises = dal.get_exercises(rand_mode)
        else:
            exercises = dal.get_exercises(mode)

        if not len(exercises):
            io.write_line('add exercises first')
            return

        exercise: str = None
        if mode == 'random':
            exercise = exercises[randint(0, len(exercises) - 1)]

            title = '%s (%s)'%(exercise, rand_mode)
            if io.read_selection(('yes', 'no'), title) == 'no':
                continue

            mode = rand_mode
        else:
            exercise = io.read_selection(exercises, 'which')

        event = Event(
            mode=mode,
            exercise=exercise,
            value=0,
            when=datetime.now()
        )
        if event.is_rep:
            with io.temporary_line('how many?'):
                event.value = io.read_int(min=1)
        else:
            delay = dal.config.timer_delay_seconds
            start = datetime.now()

            with io.temporary_line('get ready...'), io.timer(delay):
                io.read_any()

            event.value = (datetime.now() - start).seconds - delay
            if event.value < 0:
                io.write_line('canceled %s', exercise)
                continue

        io.write_line('+ %s', io.format_event(event))
        dal.push_event(event)
        dal.commit()
