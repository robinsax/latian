from datetime import datetime
from typing import ContextManager

from ..io import IO
from ..dal import DAL
from ..model import SessionPlan, Exercise, Event, Config

def temporary_show_session_plan(
    io: IO, plan: SessionPlan
) -> ContextManager:
    io.write_message(plan.name)
    for exercise in plan.exercises:
        io.write_exercise(exercise, prefix='-')

    return io.temporary_messages(len(plan.exercises) + 1)

async def run_exercise(
    io: IO, dal: DAL, config: Config, exercise: Exercise
):
    event = Event(
        type=exercise.type,
        exercise=exercise.name,
        value=0,
        when=datetime.now()
    )
    if event.is_rep:
        event.value = await io.read_int('how many?', min=0)
    else:
        start = datetime.now()

        with io.timer(config.timer_delay_seconds):
            await io.read_signal()
        event.value = (
            (datetime.now() - start).seconds -
            config.timer_delay_seconds
        )
    if event.value <= 0:
        return

    totals = await dal.compute_exercise_totals(exercise.type)
    if event.is_milestone(totals[exercise.name], config):
        dummy_event = Event(
            exercise='milestone %s!'%exercise.name,
            type=exercise.type,
            value=totals[exercise.name] + event.value
        )
        io.write_event(dummy_event, prefix='+')
    else:
        io.write_event(event, prefix='+')

    await dal.create_event(event)
    await dal.commit()
