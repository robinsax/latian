from datetime import datetime

from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, Event
from . import actions

@actions.implementation('view report')
async def report_action(dal: DAL, io: IO):
    last_when = datetime(year=2000, month=1, day=1)

    exercise_count = 0
    exercises_by_type: dict[str, list[Exercise]] = dict()
    for type in EXERCISE_TYPES:
        exercises_by_type[type] = await dal.get_exercises(type)
        exercise_count += len(exercises_by_type[type])

    events = await dal.get_events()

    temp_messages = len(events) + exercise_count + 6
    with io.temporary_messages(temp_messages):
        io.write_message('-- log --')
        for event in events:
            if not last_when or last_when.date() != event.when.date():
                io.write_message(event.when.strftime('%d/%m/%Y'))

            io.write_event(event, prefix=event.when.strftime('%H:%M'))
            last_when = event.when

        io.write_message('-- totals --')
        for type in EXERCISE_TYPES:
            io.write_message('- %s -', type)

            totals = await dal.compute_exercise_totals(type)

            for exercise in exercises_by_type[type]:
                dummy_event = Event(
                    type=type,
                    exercise=exercise.name,
                    value=totals[exercise.name]
                )
                io.write_event(dummy_event)

        await io.read_signal()
