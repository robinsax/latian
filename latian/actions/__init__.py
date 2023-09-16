'''
Application logic is implemented as asynchronous functions that take
an I/O provider and DAL as input.
'''
from typing import Callable, Coroutine

from ..io import IO
from ..dal import DAL
from ..common import Implementations

ActionFn = Callable[[DAL, IO], Coroutine]

actions = Implementations[ActionFn]()

# Load action implementations.
from . import (
    free_session, planned_session, report, add_exercise,
    session_planner, configure
)
