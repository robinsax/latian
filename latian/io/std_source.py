from ..common import Exit
from .source import IOSource, io_sources

@io_sources.implementation('std')
class StandardIOSource(IOSource):

    def bind(self):
        pass

    def unbind(self):
        pass

    def read_blocking(self):
        try:
            return input()
        except KeyboardInterrupt:
            raise Exit()

    def write(self, string: str, formats: tuple() = None):
        if formats:
            string = string%formats
        print(string, end=str())

    def unwrite_lines(self, count: int):
        for _ in range(count):
            print('\x1b[K\x1b[A\x1b[J', end=str())
