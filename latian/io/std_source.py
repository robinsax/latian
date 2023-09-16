'''
I/O source implementation using stdin/out, the terminal.
'''
from time import sleep
from typing import Callable, Any
from threading import Thread
from datetime import datetime, timedelta

from ..model import Event, Exercise
from ..common import Exit
from .io_source import IOSource, io_sources

def _format_duration(seconds: int):
    if seconds < 0:
        return '%ds'%seconds
    return '%dm%ds'%(int(seconds/60), seconds%60)

class TimerThread(Thread):
    '''Thread that writes an updating timer to stdout.'''
    stop: bool = False
    
    def __init__(self, delay_seconds: int):
        super().__init__()
        self.start_time = (
            datetime.now() + timedelta(seconds=delay_seconds)
        )

    def stop_timer(self):
        self.stop = True

    def run(self):
        while not self.stop:
            now = datetime.now()
            seconds = (now - self.start_time).seconds
            if now < self.start_time:
                seconds = -(self.start_time - now).seconds

            print('\r%s%s'%(
                _format_duration(seconds), ' '*10
            ), end=str())
            sleep(0.1)

@io_sources.implementation('std')
class StandardIOSource(IOSource):

    async def bind(self):
        pass

    async def unbind(self):
        pass

    async def read_input(
        self,
        message: str = None,
        signal_only: bool = False,
        options: list[str] = None,
        validator_fn: Callable[[str], Any] = None
    ) -> Any:
        temp_messages = 0
        if message:
            if options:
                message = '%s:'%message
            self.write_message(message)
            temp_messages += 1
        if options:
            def validate_choice(input_str):
                index = int(input_str)
                if index < 1 or index > len(options):
                    raise ValueError()
                return options[index - 1]
            validator_fn = validate_choice
            
            for k, option in enumerate(options):
                self.write_message('  %d: %s'%(k + 1, option))
            temp_messages += len(options)

        try:
            failed_validate = False
            value = None
            while True:
                prompt = '> '
                if signal_only:
                    prompt = 'press enter...'
                elif failed_validate:
                    prompt = 'try again %s'%prompt

                try:
                    value = input(prompt)
                except (KeyboardInterrupt, EOFError):
                    if not signal_only:
                        print()
                    raise Exit()
                finally:
                    self.unwrite_messages(1)

                if signal_only:
                    break

                try:
                    if validator_fn:
                        value = validator_fn(value)
                    break
                except ValueError:
                    failed_validate = True
        finally:
            self.unwrite_messages(temp_messages)

        return value

    def write_message(self, message: str):
        print(message)

    def write_event(self, event: Event, prefix: str = None):
        message = '%s%s'%(
            event.exercise,
            ' '*(40 - len(event.exercise))
        )
        if prefix:
            message = '%s %s'%(prefix, message)

        if event.is_rep:
            message = '%sx%d'%(message, event.value)
        else:
            message = '%s%s'%(message, _format_duration(event.value))

        self.write_message(message)

    def write_exercise(self, exercise: Exercise, prefix: str):
        message = '%s (%s)'%(exercise.name, exercise.type)
        if prefix:
            message = '%s %s'%(prefix, message)

        self.write_message(message)

    def write_timer(self, delay_seconds: int) -> Callable:
        timer_thread = TimerThread(delay_seconds)
        timer_thread.start()

        def stop():
            timer_thread.stop_timer()
        return stop

    def unwrite_messages(self, count: int):
        for _ in range(count):
            print('\x1b[K\x1b[A\x1b[J', end=str())
