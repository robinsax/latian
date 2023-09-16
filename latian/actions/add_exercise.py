from ..io import IO
from ..dal import DAL
from ..model import EXERCISE_TYPES, Exercise
from . import actions

@actions.implementation('add exercise')
async def add_exercise_action(dal: DAL, io: IO):
    with io.temporary_write() as temp_out:
        temp_out.write_message('- new exercise -')

        type = await io.read_choice(
            EXERCISE_TYPES, 'type', with_cancel=True
        )
        name = await io.read_string('name')

        await dal.create_exercise(Exercise(
            type=type,
            name=name
        ))

    await dal.commit()
