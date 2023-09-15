'''
Factory that collects the configured application in an asynchonous
callable.
'''
import sys
from typing import Callable, Coroutine

from .dal import DAL, storage_backends
from .io import IO, io_sources
from .cli import CLIArgs
from .model import get_schema
from .actions import actions
from .runtime import runtimes

def create_application() -> Callable[[], Coroutine]:
    args = CLIArgs(sys.argv[1:], {
        'help': (
            ('--help', '-h'),
            'show the help text',
            dict()
        ),
        'io': (
            ('--io', '-i'),
            'specify io type',
            {
                'value': io_sources.names,
                'default': io_sources.names[0]
            }
        ),
        'storage': (
            ('--storage', '-s'),
            'specify storage type',
            {
                'value': storage_backends.names,
                'default': storage_backends.names[0]
            }
        ),
        'storage_dest': (
            ('--storage-dest', '-d'),
            'specify storage location',
            {
                'value': str,
                'default': lambda args: \
                    '.' \
                    if args.get('storage') == 'file' \
                    else None
            }
        ),
        'runtime': (
            ('--runtime', '-r'),
            'specify runtime type',
            {
                'value': runtimes.names,
                'default': runtimes.names[0]
            }
        ),
        'port': (
            ('--port', '-p'),
            'specify port for network io',
            {
                'value': int,
                'default': 5000
            }
        )
    })
    
    if args.get('help'):
        args.show_help()
        sys.exit(0)

    StorageBackendImpl = storage_backends.get(args.get('storage'))
    IOSourceImpl = io_sources.get(args.get('io'))
    RuntimeImpl = runtimes.get(args.get('runtime'))

    def dal_factory():
        return DAL(StorageBackendImpl(get_schema(), args))
    def io_factory():
        return IO(IOSourceImpl(args))

    runtime = RuntimeImpl(dal_factory, io_factory, args)

    async def run():
        await runtime.run(actions)
    return run
