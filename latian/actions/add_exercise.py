from ..io import IO
from ..dal import DAL
from ..common import MODES
from . import actions

@actions.implementation('add exercise')
async def add_exercise_action(dal: DAL, io: IO):
    with io.temporary_message('describe it'):
        mode = await io.read_selection(MODES, 'mode')
        exercise = await io.read_string('name')

        dal.push_exercise(mode, exercise)

    dal.commit()
