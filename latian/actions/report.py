from datetime import datetime

from ..io import IO
from ..dal import DAL, Event
from ..common import MODES
from . import actions

@actions.implementation('report')
def report_action(dal: DAL, io: IO):
    last_when = datetime(year=2000, month=1, day=1)

    io.write_line('-- log')
    for event in dal.events:
        if not last_when or last_when.date() != event.when.date():
            io.write_line(event.when.strftime('%d/%m/%Y'))

        io.write_line('%s %s', event.when.strftime('%H:%M'), io.format_event(event))
        last_when = event.when

    io.write_line('\n-- totals')
    for mode in MODES:
        io.write_line('- %s', mode)

        totals = dal.compute_event_totals(mode)
        exercises = dal.get_exercises(mode)

        for exercise in exercises:
            dummy_event = Event(
                mode=mode,
                exercise=exercise,
                value=totals[exercise]
            )
            io.write_line(io.format_event(dummy_event))

    io.write_line(str())
