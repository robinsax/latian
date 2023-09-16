from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise, SessionPlan
from . import actions

# TODO: Updates.

@actions.implementation('session planner')
async def session_planner_action(dal: DAL, io: IO):
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

    with io.temporary() as tmp_io:
        tmp_io.write_message('- new session plan -')

        plan_name = await io.read_string('name')
        tmp_io.write_message(plan_name)

        exercises = list()
        while True:
            type = await io.read_choice(
                (*allowed_types, 'done'), 'exercise type'
            )
            if type == 'done':
                break
            exercise_name = await io.read_choice(
                (*exercise_names_by_type[type], 'back'), 'which'
            )
            if exercise_name == 'back':
                continue

            exercise = Exercise(
                type=type,
                name=exercise_name
            )
            exercises.append(exercise)
            tmp_io.write_exercise(exercise)

        await dal.create_session_plan(SessionPlan(
            name=plan_name,
            exercises=exercises
        ))

    await dal.commit()
