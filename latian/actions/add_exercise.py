from ..io import IO
from ..dal import DAL
from ..common import MODES
from . import actions

@actions.implementation('add exercise')
def add_exercise_action(dal: DAL, io: IO):
    with io.temporary_line('describe it'):
        mode = io.read_selection(MODES, 'mode')

        with io.temporary_line('name:'):
            dal.push_exercise(mode, io.read_string())

    dal.commit()
