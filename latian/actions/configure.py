from ..io import IO
from ..dal import DAL
from ..model import CONFIG_TITLES, Config
from . import actions

@actions.implementation('configure')
async def configure_action(dal: DAL, io: IO):
    with io.temporary_write() as temp_out:
        temp_out.write_message('- configuration -')

        config = Config(loaded=True)
        schema = Config.schema()
        for key in schema:
            if key == 'loaded':
                continue

            type = schema[key]
            title = CONFIG_TITLES[key]

            value = None
            if type is str:
                value = await io.read_string(title)
            elif type is int:
                value = await io.read_int(title, min=1)
            else:
                raise TypeError()

            setattr(config, key, value)

    await dal.set_config(config)
    await dal.commit()
