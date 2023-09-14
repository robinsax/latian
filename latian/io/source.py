from ..common import ImplementationRegistry

io_sources = ImplementationRegistry()

class IOSource:
    '''Text-based user IO provider.'''
    cli_args = None

    def __init__(self, cli_args):
        self.cli_args = cli_args

    def bind(self):
        raise NotImplementedError()
    
    def unbind(self):
        raise NotImplementedError()

    def read_blocking(self):
        raise NotImplementedError()
    
    def write(self, string: str, formats: tuple() = None):
        raise NotImplementedError()

    def unwrite_lines(self, count: int):
        raise NotImplementedError()
