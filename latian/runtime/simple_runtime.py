from ..common import Exit
from .runtime import Runtime, runtimes

@runtimes.implementation('simple')
class SimpleRuntime(Runtime):
    
    def run(self):
        self.io.bind()
        self.dal.connect()

        try:
            if not self.dal.config.loaded:
                self.actions.get('configure')(self.dal, self.io)

            while True:            
                action_name = self.io.read_selection(
                    self.actions.names, 'what to do'
                )

                self.actions.get(action_name)(self.dal, self.io)
        except Exit:
            self.io.write_line(self.dal.config.exit_message)
        finally:
            self.io.unbind()
