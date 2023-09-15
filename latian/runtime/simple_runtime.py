from ..common import Exit
from .runtime import Runtime, runtimes

@runtimes.implementation('simple')
class SimpleRuntime(Runtime):
    
    async def run(self):
        await self.io.bind()
        self.dal.connect()

        try:
            if not self.dal.config.loaded:
                await self.actions.get('configure')(self.dal, self.io)

            while True:
                action_name = await self.io.read_selection(
                    self.actions.names, 'what to do'
                )

                await self.actions.get(action_name)(self.dal, self.io)
        except Exit:
            self.io.write_message(self.dal.config.exit_message)
        finally:
            await self.io.unbind()
