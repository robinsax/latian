from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, SessionPlan
from .common import temporary_show_session_plan, run_exercise
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
        with temporary_show_session_plan(io, plan):
            confirm = await io.read_choice(('yes', 'no'), 'this?')
            if confirm == 'yes':
                break

    for exercise in plan.exercises:
        with io.temporary_messages(2):
            io.write_message('next exercise')
            io.write_exercise(exercise)
            await io.read_signal()

        await run_exercise(io, dal, config, exercise)

    io.unwrite_messages(len(plan.exercises))

    await io.read_signal('done session plan')
