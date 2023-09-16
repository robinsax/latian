from datetime import datetime, date

from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, Event
from . import actions

@actions.implementation('view report')
async def report_action(dal: DAL, io: IO):
    last_when = datetime(year=2000, month=1, day=1)

    report_type = await io.read_choice(
        ('log', 'totals'), 'report type'
    )
    report_span = await io.read_choice(
        ('daily', 'all time'), 'timespan'
    )
    query_args = dict()
    if report_span == 'daily':
        query_args['day'] = date.today()

    if report_type == 'log':
        events = await dal.get_events(**query_args)

        last_date = date(year=2000, month=1, day=1)
        to_write = list()
        for event in events:
            event_date = event.when.date()
            if not last_date or last_date != event_date:
                to_write.append(event_date.strftime('%d/%m/%Y'))

            to_write.append(event)
            last_date = event_date

        with io.temporary_messages(len(to_write) + 1):
            io.write_message('- log -')

            for item in to_write:
                if isinstance(item, str):
                    io.write_message(item)
                    continue

                prefix = item.when.strftime('%H:%M')
                io.write_event(item, prefix=prefix)

            await io.read_signal()
    else:
        totals_by_type = dict()
        exercises_by_type = dict()
        totals_count = 0
        for type in EXERCISE_TYPES:
            exercises_by_type[type] = await dal.get_exercises(type)
            totals_by_type[type] = await dal.compute_exercise_totals(
                type, **query_args
            )
            totals_count += len(totals_by_type[type])

        with io.temporary_messages(totals_count + 3):
            io.write_message('- totals -')
            
            for type in EXERCISE_TYPES:
                io.write_message(type)

                for exercise in exercises_by_type[type]:
                    dummy_event = Event(
                        type=type,
                        exercise=exercise.name,
                        value=totals_by_type[type][exercise.name]
                    )
                    io.write_event(dummy_event)

            await io.read_signal()
