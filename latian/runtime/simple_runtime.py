'''
A runtime that can handle a single default user, once.
'''
from ..model import create_default_config
from ..actions import ActionFn
from ..common import Exit, Implementations
from .runtime import Runtime, runtimes

@runtimes.implementation('simple')
class SimpleRuntime(Runtime):

    async def run(self, actions: Implementations[ActionFn]):
        io = self.io_factory()
        dal = self.dal_factory()

        await io.bind()
        await dal.connect(self.args.get('user'))

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
            await io.unbind()
            await dal.disconnect()
