import sys

from .dal import DAL, storage_backends
from .io import IO, io_sources
from .cli import CLIArgs
from .actions import actions
from .runtime import Runtime, runtimes

def initialize() -> Runtime:
    args = CLIArgs(sys.argv[1:], {
        'help': (
            ('--help', '-h'),
            'show the help text',
            dict()
        ),
        'io': (
            ('--io', '-i'),
            'specify i/o type',
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
                'default': (
                    lambda args: \
                        'db.json' \
                        if args.get('storage') == 'file' \
                        else None
                )
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

    IOSourceImpl = io_sources.get(args.get('io'))
    StorageBackendImpl = storage_backends.get(args.get('storage'))
    RuntimeImpl = runtimes.get(args.get('runtime'))

    io = IO(IOSourceImpl(args))
    dal = DAL(StorageBackendImpl(args.get('storage_dest')))

    return RuntimeImpl(dal, io, actions)
