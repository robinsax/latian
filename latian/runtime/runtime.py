'''
Abstract base and implementation registry for runtimes.
'''
from typing import Type, Callable

from ..io import IO
from ..dal import DAL
from ..cli import CLIArgs
from ..model import create_default_config
from ..actions import ActionFn
from ..common import Implementations, Exit, Reset

class Runtime:
    io_factory: Callable[[], IO]
    dal_factory: Callable[[], DAL]
    args: CLIArgs

    def __init__(
        self,
        dal_factory: Callable[[], DAL],
        io_factory: Callable[[], IO],
        args: CLIArgs
    ):
        self.dal_factory = dal_factory
        self.io_factory = io_factory
        self.args = args
    
    async def run(self, actions: Implementations[ActionFn]):
        raise NotImplementedError()

    async def run_user_standard(
        self, dal: DAL, io: IO, actions: Implementations[ActionFn]
    ):
        config = await dal.get_config()
        if not config:
            config = create_default_config()
            await dal.set_config(config)

        try:
            if not config.loaded:
                with io.temporary_write() as temp_out:
                    temp_out.write_message('let\'s set things up')

                    await actions.get('configure')(dal, io)
                    config = await dal.get_config()

            while True:
                action = await io.read_choice(
                    actions.names, 'what do you want to do'
                )

                try:
                    await actions.get(action)(dal, io)
                except Reset:
                    continue

                if action == 'configure':
                    config = await dal.get_config()
        except Exit:
            io.write_message(config.exit_message)
        finally:
            await dal.disconnect()
            await io.unbind()

runtimes = Implementations[Type[Runtime]]()
