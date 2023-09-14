from time import sleep
from datetime import datetime, timedelta
from threading import Thread

from ..model import Event
from ..common import Exit
from .source import IOSource, io_sources

from . import std_source, http_source

class IO:
    _source: IOSource = None

    def __init__(self, source: IOSource):
        self._source = source

    def bind(self):
        self._source.bind()

    def unbind(self):
        self._source.unbind()

    # Formatting.
    def format_seconds(self, seconds: str):
        if seconds < 0:
            return '%ds'%seconds
        return '%dm%ds'%(int(seconds/60), seconds%60)
    
    def format_event(self, event: Event):
        base = '%s%s'%(event.exercise, ' '*(40 - len(event.exercise)))

        if event.mode == 'rep':
            return '%sx%d'%(base, event.value)
        else:
            return '%s%s'%(base, self.format_seconds(event.value))
    
    # Output.
    def write(self, string: str, *formats: list):
        self._source.write(string, formats)

    def write_line(self, string: str, *formats: list):
        self.write('%s\n'%string, *formats)

    def unwrite_lines(self, count: int):
        self._source.unwrite_lines(count)

    # Output contexts.
    def temporary_lines(self, count: int) -> 'LineClearContext':
        return LineClearContext(self, count)
    
    def temporary_line(self, string: str, *formats: list) -> 'LineClearContext':
        self.write_line(string, *formats)
        return self.temporary_lines(1)
    
    def timer(self, delay_seconds: int) -> 'TimerContext':
        return TimerContext(self, delay_seconds)
    
    # Input.
    def _read_validated(self, parser_fn):
        failed = False
        while True:
            self.write('try again > ' if failed else '> ')
            try:
                value = parser_fn(self._source.read_blocking())
                self.unwrite_lines(1)

                return value
            except ValueError:
                self.unwrite_lines(1)
                failed = True
            except Exit:
                self.write_line(str())
                self.unwrite_lines(1)
                raise

    def read_any(self):
        try:
            self._source.read_blocking()
            self.unwrite_lines(1)
        except Exit:
            self.write_line(str())
            self.unwrite_lines(1)
            raise

    def read_string(self) -> str:
        def validator(value):
            if not len(value):
                raise ValueError()
            return value
        
        return self._read_validated(validator)

    def read_int(self, min=0, max=-1) -> int:
        def validator(value):
            value = int(value)
            if value < min or (max >= 0 and value > max):
                raise ValueError()
            return value
        
        return self._read_validated(validator)

    def read_selection(self, options: list, title: str) -> str:
        with self.temporary_lines(len(options) + 1):
            self.write_line('pick %s:'%title)
            for k, option in enumerate(options):
                self.write_line('  %d: %s'%(k + 1, option))
            
            picked = self.read_int(min=1, max=len(options)) - 1

        return options[picked]

class LineClearContext:
    io: IO = None
    count: int = 0

    def __init__(self, io: IO, count: int):
        self.io = io
        self.count = count

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not exc_value or isinstance(exc_value, Exit):
            self.io.unwrite_lines(self.count)

class TimerThread(Thread):
    io: IO = None
    stop: bool = False
    
    def __init__(self, io: IO, delay_seconds: int):
        super().__init__()
        self.io = io
        self.start_time = datetime.now() + timedelta(seconds=delay_seconds)

    def stop_timer(self):
        self.stop = True

    def run(self):
        while not self.stop:
            now = datetime.now()
            seconds = (now - self.start_time).seconds
            if now < self.start_time:
                seconds = -(self.start_time - now).seconds

            self.io.write('\r%s%s'%(self.io.format_seconds(seconds), ' '*10))
            sleep(0.1)

class TimerContext:
    thread: TimerThread = None

    def __init__(self, io: IO, delay_seconds: int):
        self.thread = TimerThread(io, delay_seconds)

    def __enter__(self):
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.thread.stop_timer()
