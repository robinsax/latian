'''
Abstract base and implementation registry of I/O sources.
'''
from typing import Callable, Type, Any

from ..cli import CLIArgs
from ..model import Event
from ..common import Implementations

class IOSource:
    args: CLIArgs

    def __init__(self, args: CLIArgs):
        self.args = args

    async def bind(self):
        raise NotImplementedError()
    
    async def unbind(self):
        raise NotImplementedError()

    async def read_input(
        self,
        message: str = None,
        signal_only: bool = False,
        options: list[str] = None,
        validator_fn: Callable[[str], Any] = None
    ) -> Any:
        raise NotImplementedError()

    def write_message(self, message: str):
        raise NotImplementedError()
    
    def write_timer(self, delay_seconds: int) -> Callable:
        raise NotImplementedError()
    
    def write_event(self, event: Event, prefix: str):
        raise NotImplementedError()

    def unwrite_messages(self, count: int):
        raise NotImplementedError()

io_sources = Implementations[Type[IOSource]]()
