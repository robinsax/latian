from typing import Callable, Any

from ..common import ImplementationRegistry
from ..model import Event

io_sources = ImplementationRegistry()

class IOSource:
    cli_args = None

    def __init__(self, cli_args):
        self.cli_args = cli_args

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
