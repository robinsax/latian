from typing import Callable

from ..model import Event
from ..common import Exit
from .source import IOSource, io_sources

from . import std_source, ws_source

class MessageUnwriteContext:
    io: 'IO' = None
    count: int = 0

    def __init__(self, io: 'IO', count: int):
        self.io = io
        self.count = count

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_value or isinstance(exc_value, Exit):
            self.io.unwrite_messages(self.count)

class TimerStopContext:
    stop_fn: Callable = None

    def __init__(self, stop_fn: Callable):
        self.stop_fn = stop_fn

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop_fn()

class IO:
    _source: IOSource = None
    _line_count: int = 0

    def __init__(self, source: IOSource):
        self._source = source
        self._line_count = -1

    async def bind(self):
        await self._source.bind()

    async def unbind(self):
        await self._source.unbind()

    # Output.
    def write_message(self, message: str, *formats: list):
        if formats:
            message = message%formats
        self._source.write_message(message)

    def write_event(self, event: Event, prefix: str = None):
        self._source.write_event(event, prefix)

    def unwrite_messages(self, count: int):
        self._source.unwrite_messages(count)

    # Output contexts.
    def temporary_messages(self, count: int) -> MessageUnwriteContext:
        return MessageUnwriteContext(self, count)
    
    def temporary_message(self, string: str, *formats: list) -> MessageUnwriteContext:
        self.write_message(string, *formats)
        return self.temporary_messages(1)
    
    def timer(self, delay_seconds: int) -> TimerStopContext:
        return TimerStopContext(self._source.write_timer(delay_seconds))
    
    # Input.
    async def read_signal(self, message: str = None):
        await self._source.read_input(
            message=message,
            signal_only=True
        )

    async def read_string(self, message: str = None) -> str:
        def validator(value):
            if not len(value):
                raise ValueError()
            return value
        
        return await self._source.read_input(
            message=message,
            validator_fn=validator
        )

    async def read_int(self, message: str = None, min=0, max=-1) -> int:
        def validator(value):
            value = int(value)
            if value < min or (max >= 0 and value > max):
                raise ValueError()
            return value
        
        return await self._source.read_input(
            message=message,
            validator_fn=validator
        )

    async def read_selection(self, options: list[str], message: str = None) -> str:
        return await self._source.read_input(
            message=message,
            options=options
        )
