'''
Application logic is implemented as asynchronous functions that take
an I/O provider and DAL as input.
'''
from typing import Callable, Coroutine

from ..io import IO
from ..dal import DAL
from ..common import ImplementationRegistry

ActionFn = Callable[[DAL, IO], Coroutine]

actions = ImplementationRegistry[ActionFn]()

# Load action implementations.
from . import session, report, add_exercise, configure
