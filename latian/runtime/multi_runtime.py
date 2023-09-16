'''
A runtime that can serve multiple different users concurrently.
'''
import asyncio

from ..io import IO
from ..actions import ActionFn
from ..common import Implementations
from .runtime import Runtime, runtimes

@runtimes.implementation('multi')
class MultiUserRuntime(Runtime):

    async def run(self, actions: Implementations[ActionFn]):
        while True:
            io = self.io_factory()
            await io.bind()

            asyncio.create_task(self.run_one(io, actions))

    async def run_one(
        self, io: IO, actions: Implementations[ActionFn]
    ):
        dal = self.dal_factory()

        user = await io.read_string('who are you?')
        await dal.connect(user)

        await self.run_user_standard(dal, io, actions)
