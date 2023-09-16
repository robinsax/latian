'''
A runtime that can handle a single default user, once.
'''
from ..actions import ActionFn
from ..common import Implementations
from .runtime import Runtime, runtimes

@runtimes.implementation('simple')
class SimpleRuntime(Runtime):

    async def run(self, actions: Implementations[ActionFn]):
        io = self.io_factory()
        dal = self.dal_factory()

        await io.bind()
        await dal.connect(self.args.get('user'))

        await self.run_user_standard(dal, io, actions)
