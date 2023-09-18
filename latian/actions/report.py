from datetime import timedelta, date

from ..io import IO, IOWriter
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, Event
from . import actions

async def _report_log(
    dal: DAL, out: IOWriter, base_day: date = None
):
    events = await dal.get_events(day=base_day)

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

async def _report_totals(
    dal: DAL, out: IOWriter, base_day: date = None
):
    out.write_message('- totals -')
    if base_day:
        out.write_message(base_day.strftime('%d/%m/%Y'))

    for type in EXERCISE_TYPES:
        exercises = await dal.get_exercises(type)

        for exercise in exercises:
            total = await dal.get_exercise_total(
                exercise, day=base_day
            )
            dummy_event = Event(
                type=type,
                exercise=exercise.name,
                value=total
            )
            out.write_event(dummy_event)

async def _report_difference(
    dal: DAL, out: IOWriter, base_day: date
):
    events_this = await dal.get_events(day=base_day)
    events_prev = await dal.get_events(
        day=base_day - timedelta(days=1)
    )

    def totals_in(set: list[Event], exercise: Exercise):
        total = 0
        for event in set:
            if not event.is_exercise(exercise):
                continue

            total += event.value

        return total

    out.write_message('- daily difference -')
    out.write_message(base_day.strftime('%d/%m/%Y'))
    out.write_message('events day before: %d', len(events_prev))
    out.write_message('events this day: %d', len(events_this))

    for type in EXERCISE_TYPES:
        exercises = await dal.get_exercises(type)

        for exercise in exercises:
            dummy_event = Event(
                type=type,
                exercise=exercise.name,
                value=(
                    totals_in(events_this, exercise) - \
                    totals_in(events_prev, exercise)
                )
            )
            out.write_event(dummy_event, prefix='+/-')

@actions.implementation('view report')
async def report_action(dal: DAL, io: IO):
    report_span = await io.read_choice(
        ('daily', 'all time'), 'timespan', with_cancel=True
    )

    day_minus = 0
    report_types = ['log', 'totals']
    if report_span == 'daily':
        report_types.append('difference')

        day_minus = await io.read_int('for how many days ago?')
        
    report_type = await io.read_choice(
        report_types, 'report type', with_cancel=True
    )

    base_day = None
    if report_span == 'daily':
        base_day = date.today() - timedelta(days=day_minus)

    with io.temporary_write() as temp_out:
        if report_type == 'difference':
            await _report_difference(dal, temp_out, base_day)
        elif report_type == 'log':
            await _report_log(dal, temp_out, base_day)
        else:
            await _report_totals(dal, temp_out, base_day)

        await io.read_signal()
