from ..io import IO
from ..dal import DAL
from ..model import Config
from . import actions

@actions.implementation('configure')
async def configure_action(dal: DAL, io: IO):
    with io.temporary_message('let\'s set things up'):
        for attr in Config.attributes():
            if attr.name == 'loaded':
                continue

            attr_type = Config.__annotations__[attr.name]
            attr_title = ' '.join(attr.name.split('_'))

            value = None
            if attr_type is str:
                value = await io.read_string(attr_title)
            elif attr_type is int:
                value = await io.read_int(attr_title, min=1)
            else:
                raise TypeError()

            dal.update_config(attr.name, value)

    dal.update_config('loaded', True)
    dal.commit()
