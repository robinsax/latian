from ..dal import DAL
from ..io import IO
from ..common import ImplementationRegistry

runtimes = ImplementationRegistry()

class Runtime:
    dal: DAL = None
    io: IO = None
    actions: ImplementationRegistry = None

    def __init__(self, dal: DAL, io: IO, actions: ImplementationRegistry):
        self.dal = dal
        self.io = io
        self.actions = actions
    
    async def run(self):
        raise NotImplementedError()
