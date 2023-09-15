from datetime import datetime

from ..io import IO
from ..dal import DAL, Event
from ..common import MODES
from . import actions

@actions.implementation('view report')
async def report_action(dal: DAL, io: IO):
    last_when = datetime(year=2000, month=1, day=1)

    temp_messages = (
        len(dal.events) +
        sum(len(dal.get_exercises(mode)) for mode in MODES) +
        6
    )
    with io.temporary_messages(temp_messages):
        io.write_message('-- log')
        for event in dal.events:
            if not last_when or last_when.date() != event.when.date():
                io.write_message(event.when.strftime('%d/%m/%Y'))

            io.write_event(event, prefix=event.when.strftime('%H:%M'))
            last_when = event.when

        io.write_message('\n-- totals')
        for mode in MODES:
            io.write_message('- %s', mode)

            totals = dal.compute_event_totals(mode)
            exercises = dal.get_exercises(mode)

            for exercise in exercises:
                dummy_event = Event(
                    mode=mode,
                    exercise=exercise,
                    value=totals[exercise]
                )
                io.write_event(dummy_event)

        await io.read_signal()
