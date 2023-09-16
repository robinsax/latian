'''
The user I/O provider for application logic.
'''
from typing import Callable, ContextManager

from latian.model import Event, Exercise

from ..model import Event, Exercise
from ..common import Reset
from .io_source import IOSource

class IOWriter:
    _source: IOSource

    def __init__(self, source: IOSource):
        self._source = source

    def write_message(self, message: str, *formats: list):
        if formats:
            message = message%formats
        self._source.write_message(message)

    def write_event(self, event: Event, prefix: str = None):
        self._source.write_event(event, prefix)

    def write_exercise(self, exercise: Exercise, prefix: str = None):
        self._source.write_exercise(exercise, prefix)

class TempIOWriterContext(IOWriter):
    '''
    Context manager for writing messages that unwrite after the block
    ends.
    '''
    count: int

    def __init__(self, source: IOSource):
        super().__init__(source)
        self.count = 0

    def __enter__(self) -> IOWriter:
        return self
    
    def __exit__(self, ExType, exc_value, exc_traceback):
        self._source.unwrite_messages(self.count)

        if ExType:
            raise ExType(exc_value).with_traceback(exc_traceback)

    def write_message(self, message: str, *formats: list):
        self.count += 1

        return super().write_message(message, *formats)
    
    def write_event(self, event: Event, prefix: str = None):
        self.count += 1

        return super().write_event(event, prefix)
    
    def write_exercise(self, exercise: Exercise, prefix: str = None):
        self.count += 1

        return super().write_exercise(exercise, prefix)

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

class IO(IOWriter):

    async def bind(self):
        await self._source.bind()

    async def unbind(self):
        await self._source.unbind()

    def temporary_write(self) -> ContextManager[IOWriter]:
        return TempIOWriterContext(self._source)

    def timer(self, delay_seconds: int) -> ContextManager:
        return TimerUnwriteContext(
            self._source.write_timer(delay_seconds)
        )
    
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
        self, options: list[str], message: str = None, *,
        control_options: list[str] = None,
        with_cancel: bool = False
    ) -> str:
        if not control_options:
            control_options = list()
        if with_cancel:
            control_options = (*control_options, 'cancel')
        
        options = list(options)
        control_lookup = dict()
        for option in control_options:
            escaped_option = '<%s>'%option
            control_lookup[escaped_option] = option
            options.append(escaped_option)

        result = await self._source.read_input(
            message=message,
            options=options
        )

        if with_cancel and result == '<cancel>':
            raise Reset()
        
        return control_lookup.get(result, result)

    async def read_confirm(self, message: str = None) -> bool:
        confirm = await self.read_choice(('yes', 'no'), message)

        return confirm == 'yes'