'''
A runtime that can serve multiple different users concurrently.
'''
import asyncio

from ..io import IO
from ..model import create_default_config
from ..actions import ActionFn
from ..common import Exit, Implementations
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
        print('%s connected'%user)
        await dal.connect(user)

        config = await dal.get_config()
        if not config:
            config = create_default_config()
            await dal.set_config(config)

        try:
            if not config.loaded:
                await actions.get('configure')(dal, io)
                config = await dal.get_config()

            while True:
                action = await io.read_choice(
                    actions.names, 'what to do'
                )

                await actions.get(action)(dal, io)
                if action == 'configure':
                    config = await dal.get_config()
        except Exit:
            io.write_message(config.exit_message)
        finally:
            await dal.disconnect()
            await io.unbind()