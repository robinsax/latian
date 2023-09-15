'''
Abstract base and implementation registry for runtimes.
'''
from typing import Type, Callable

from ..io import IO
from ..dal import DAL
from ..cli import CLIArgs
from ..actions import ActionFn
from ..common import ImplementationRegistry

class Runtime:
    io_factory: Callable[[], IO]
    dal_factory: Callable[[], DAL]
    args: CLIArgs

    def __init__(
        self,
        dal_factory: Callable[[], DAL],
        io_factory: Callable[[], IO],
        args: CLIArgs
    ):
        self.dal_factory = dal_factory
        self.io_factory = io_factory
        self.args = args
    
    async def run(self, actions: ImplementationRegistry[ActionFn]):
        raise NotImplementedError()

runtimes = ImplementationRegistry[Type[Runtime]]()
