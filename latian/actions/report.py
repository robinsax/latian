from datetime import timedelta, date

from ..io import IO, IOWriter
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, Event
from . import actions

async def _report_log(dal: DAL, out: IOWriter, query_args: dict):
    events = await dal.get_events(**query_args)

    out.write_message('- log -')

    last_date = date(year=2000, month=1, day=1)
    for event in events:
        event_date = event.when.date()
        if last_date != event_date:
            out.write_message(
                event_date.strftime('%d/%m/%Y')
            )

        out.write_event(
            event,
            prefix=event.when.strftime('%H:%M')
        )
        last_date = event_date

async def _report_totals(dal: DAL, out: IOWriter, query_args: dict):
    out.write_message('- totals -')
    
    for type in EXERCISE_TYPES:
        exercises = await dal.get_exercises(type)

        for exercise in exercises:
            total = await dal.get_exercise_total(
                exercise, **query_args
            )
            dummy_event = Event(
                type=type,
                exercise=exercise.name,
                value=total
            )
            out.write_event(dummy_event)

async def _report_difference(dal: DAL, out: IOWriter):
    today = date.today()
    events_today = await dal.get_events(day=today)
    events_yesterday = await dal.get_events(
        day=today - timedelta(days=1)
    )

    def totals_in(set: list[Event], exercise: Exercise):
        total = 0
        for event in set:
            if not event.is_exercise(exercise):
                continue

            total += event.value

        return total

    out.write_message('- daily difference -')
    out.write_message('events yesterday: %d', len(events_yesterday))
    out.write_message('events today: %d', len(events_today))

    for type in EXERCISE_TYPES:
        exercises = await dal.get_exercises(type)

        for exercise in exercises:
            dummy_event = Event(
                type=type,
                exercise=exercise.name,
                value=(
                    totals_in(events_today, exercise) - \
                    totals_in(events_yesterday, exercise)
                )
            )
            out.write_event(dummy_event, prefix='+/-')

@actions.implementation('view report')
async def report_action(dal: DAL, io: IO):
    report_span = await io.read_choice(
        ('daily', 'all time'), 'timespan', with_cancel=True
    )

    report_types = ['log', 'totals']
    if report_span == 'daily':
        report_types.append('difference')
    report_type = await io.read_choice(
        report_types, 'report type', with_cancel=True
    )

    query_args = dict()
    if report_span == 'daily':
        query_args['day'] = date.today()

    with io.temporary_write() as temp_out:
        if report_type == 'difference':
            await _report_difference(dal, temp_out)
        elif report_type == 'log':
            await _report_log(dal, temp_out, query_args)
        else:
            await _report_totals(dal, temp_out, query_args)

        await io.read_signal()
