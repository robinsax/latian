from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, SessionPlan
from .common import read_plan_choice
from . import actions

async def _run_add(dal: DAL, io: IO):
    exercise_names_by_type = dict()
    allowed_types = list()
    for type in EXERCISE_TYPES:
        exercises = await dal.get_exercises(type)
        if not len(exercises):
            continue

        allowed_types.append(type)
        exercise_names_by_type[type] = list(
            exercise.name for exercise in exercises
        )

    with io.temporary_write() as temp_out:
        temp_out.write_message('new session plan')

        plan_name = await io.read_string('name')
        temp_out.write_message(plan_name)

        exercises = list()
        while True:
            type = await io.read_choice(
                allowed_types, 'exercise type',
                control_options=('done',), with_cancel=True
            )
            if type == 'done':
                break

            exercise_name = await io.read_choice(
                *exercise_names_by_type[type], 'which',
                control_options=('back',)
            )
            if exercise_name == 'back':
                continue

            exercise = Exercise(
                type=type,
                name=exercise_name
            )
            exercises.append(exercise)
            temp_out.write_exercise(exercise, prefix='-')

        await dal.create_session_plan(SessionPlan(
            name=plan_name,
            exercises=exercises
        ))

    await dal.commit()

async def _run_delete(dal: DAL, io: IO):
    plan = await read_plan_choice(dal, io)
    
    with io.temporary_write() as temp_out:
        temp_out.write_message(plan.name)
        for exercise in plan.exercises:
            temp_out.write_exercise(exercise, prefix='-')

        if not await io.read_confirm('delete this?'):
            return

    await dal.delete_session_plan(plan)
    await dal.commit()

@actions.implementation('session planner')
async def session_planner_action(dal: DAL, io: IO):
    with io.temporary_write() as temp_out:
        temp_out.write_message('- session planner -')

        mode = await io.read_choice(
            ('create new', 'delete'), 'do what',
            control_options=('cancel',)
        )
        if mode == 'cancel':
            return
        elif mode == 'create new':
            await _run_add(dal, io)
        else:
            await _run_delete(dal, io)
