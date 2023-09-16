from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, SessionPlan
from .common import run_exercise
from . import actions

@actions.implementation('start planned session')
async def planned_session_action(dal: DAL, io: IO):
    config = await dal.get_config()

    plan: SessionPlan = None
    plans = await dal.get_session_plans()
    if not len(plans):
        await io.read_signal('add session plan first')
        return

    plan_names = list(plan.name for plan in plans)

    while True:
        plan_name = await io.read_choice(
            (*plan_names, 'cancel'), 'which'
        )
        if plan_name == 'cancel':
            return
        
        plan = plans[plan_names.index(plan_name)]
        with io.temporary() as tmp_io:
            tmp_io.write_message(plan.name)
            for exercise in plan.exercises:
                tmp_io.write_exercise(exercise, prefix='-')

            if await io.read_confirm('this?'):
                break

    with io.temporary() as session_io:
        for exercise in plan.exercises:
            with io.temporary() as exercise_io:
                exercise_io.write_message('next exercise')
                exercise_io.write_exercise(exercise)

                await io.read_signal()

            await run_exercise(io, session_io, dal, config, exercise)

    await io.read_signal('done session plan')
