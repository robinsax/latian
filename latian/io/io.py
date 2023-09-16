'''
The user I/O provider for application logic.
'''
from typing import Callable, ContextManager

from ..model import Event, Exercise
from .io_source import IOSource

class MessageUnwriteContext:
    '''Context manager that causes message remove when it ends.'''
    io: 'IO'
    count: int

    def __init__(self, io: 'IO', count: int):
        self.io = io
        self.count = count

    def __enter__(self):
        return self
    
    def __exit__(self, ExType, exc_value, exc_traceback):
        if ExType:
            raise ExType(exc_value).with_traceback(exc_traceback)

        self.io.unwrite_messages(self.count)        

class TimerUnwriteContext:
    '''Context manager that removes a timer when it ends.'''
    stop_fn: Callable

    def __init__(self, stop_fn: Callable):
        self.stop_fn = stop_fn

    def __enter__(self):
        return self
    
    def __exit__(self, ExType, exc_value, exc_traceback):
        self.stop_fn()

        if ExType:
            raise ExType(exc_value).with_traceback(exc_traceback)

class IO:
    _source: IOSource

    def __init__(self, source: IOSource):
        self._source = source

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

    def write_exercise(self, exercise: Exercise, prefix: str = None):
        self._source.write_exercise(exercise, prefix)

    def unwrite_messages(self, count: int):
        self._source.unwrite_messages(count)

    # Output contexts.
    def temporary_messages(self, count: int) -> ContextManager:
        return MessageUnwriteContext(self, count)
    
    def temporary_message(
        self, string: str, *formats: list
    ) -> MessageUnwriteContext:
        self.write_message(string, *formats)
        return self.temporary_messages(1)
    
    def timer(self, delay_seconds: int) -> ContextManager:
        return TimerUnwriteContext(
            self._source.write_timer(delay_seconds)
        )
    
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

    async def read_int(
        self, message: str = None, min=0, max=-1
    ) -> int:
        def validator(value):
            value = int(value)
            if value < min or (max >= 0 and value > max):
                raise ValueError()
            return value
        
        return await self._source.read_input(
            message=message,
            validator_fn=validator
        )

    async def read_choice(
        self, options: list[str], message: str = None
    ) -> str:
        return await self._source.read_input(
            message=message,
            options=options
        )
