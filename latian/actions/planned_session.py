from ..io import IO
from ..dal import DAL
from ..model import SessionPlan
from .common import run_exercise, read_plan_choice
from . import actions

@actions.implementation('start planned session')
async def planned_session_action(dal: DAL, io: IO):
    config = await dal.get_config()

    plan: SessionPlan = None
    while True:
        plan = await read_plan_choice(dal, io)

        with io.temporary_write() as temp_out:
            temp_out.write_message(plan.name)
            for exercise in plan.exercises:
                temp_out.write_exercise(exercise, prefix='-')

            if await io.read_confirm('this?'):
                break

    with io.temporary_write() as session_io:
        for exercise in plan.exercises:
            with io.temporary_write() as exercise_io:
                exercise_io.write_message('next exercise')
                exercise_io.write_exercise(exercise)

                await io.read_signal()

            await run_exercise(io, session_io, dal, config, exercise)

        await io.read_signal('done session plan')
