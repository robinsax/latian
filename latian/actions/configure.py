from ..io import IO
from ..dal import DAL
from ..model import Config
from . import actions

@actions.implementation('configure')
def configure_action(dal: DAL, io: IO):
    with io.temporary_line('let\'s set things up'):
        for attr in Config.attributes():
            if attr.name == 'loaded':
                continue

            with io.temporary_line('%s:', ' '.join(attr.name.split('_'))):
                typ = Config.__annotations__[attr.name]

                value = None
                if typ is str:
                    value = io.read_string()
                elif typ is int:
                    value = io.read_int(min=1)
                else:
                    raise TypeError()

                dal.update_config(attr.name, value)

    dal.update_config('loaded', True)
    dal.commit()
