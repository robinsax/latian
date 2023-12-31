from datetime import datetime

from ..io import IO, IOWriter
from ..dal import DAL
from ..model import Exercise, Event, Config, SessionPlan
from ..common import Reset

async def read_plan_choice(dal: DAL, io: IO) -> SessionPlan:
    plans = await dal.get_session_plans()
    if not len(plans):
        await io.read_signal('add session plan first')
        raise Reset()

    plan_names = list(plan.name for plan in plans)
    plan_name = await io.read_choice(
        plan_names, 'which', with_cancel=True
    )

    return plans[plan_names.index(plan_name)]

async def run_exercise(
    io: IO, io_writer: IOWriter, dal: DAL, config: Config,
    exercise: Exercise
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

    total = await dal.get_exercise_total(exercise)
    if event.is_milestone(total, config):
        dummy_event = Event(
            exercise='milestone %s!'%exercise.name,
            type=exercise.type,
            value=total + event.value
        )
        io_writer.write_event(dummy_event, prefix='+')
    
    io_writer.write_event(event, prefix='+')

    await dal.create_event(event)
    await dal.commit()
