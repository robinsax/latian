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

        with io.temporary_write() as temp_out:
            temp_out.write_message('- log -')

            last_date = date(year=2000, month=1, day=1)
            for event in events:
                event_date = event.when.date()
                if last_date != event_date:
                    temp_out.write_message(
                        event_date.strftime('%d/%m/%Y')
                    )

                temp_out.write_event(
                    event,
                    prefix=event.when.strftime('%H:%M')
                )
                last_date = event_date

            await io.read_signal()
    else:
        totals_by_type: dict[str, int]  = dict()
        exercises_by_type: dict[str, list[Exercise]] = dict()
        for type in EXERCISE_TYPES:
            exercises_by_type[type] = await dal.get_exercises(type)
            totals_by_type[type] = await dal.compute_exercise_totals(
                type, **query_args
            )

        with io.temporary_write() as temp_out:
            temp_out.write_message('- totals -')
            
            for type in EXERCISE_TYPES:
                temp_out.write_message(type)

                for exercise in exercises_by_type[type]:
                    dummy_event = Event(
                        type=type,
                        exercise=exercise.name,
                        value=totals_by_type[type][exercise.name]
                    )
                    temp_out.write_event(dummy_event)

            await io.read_signal()
