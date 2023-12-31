'''
I/O source implementation using a WebSocket server and associated
frontend.

Transacts JSON WebSocket messages.
'''
import io
import json
import asyncio
from aiohttp import web
from asyncio import Queue
from typing import Callable, Any

from latian.model import Exercise

from ..cli import CLIArgs
from ..model import Event
from ..common import Exit
from .io_source import IOSource, io_sources

ASSET_PATH_FORMAT = 'latian/io/ws_source.%s'
CLOSE_SIGNAL = '<<close>>'

def _load_asset(extension) -> str:
    path = ASSET_PATH_FORMAT%extension
    with io.open(path, encoding='utf-8') as asset_io:
       return asset_io.read()

class WebSocketIOServer:
    '''Singleton WebSocket server.'''
    instance: 'WebSocketIOServer' = None
    args: CLIArgs
    socket_queue: Queue[tuple[Queue, Queue]]
    port: int

    @classmethod
    async def next_socket(cls, args: CLIArgs) -> tuple[Queue, Queue]:
        if not cls.instance:
            cls.instance = cls(args)
            await cls.instance.start()

        return await cls.instance.socket_queue.get()
    
    def __init__(self, args: CLIArgs):
        self.args = args
        self.socket_queue = Queue()
        self.port = self.args.get('port')

    async def get_index(self, req: web.Request):
        return web.Response(
            text=_load_asset('html'),
            content_type='text/html'
        )
    
    async def get_js(self, req: web.Request):
        return web.Response(
            text=_load_asset('js').replace('$PORT', str(self.port)),
            content_type='application/javascript'
        )

    async def handle_socket(self, req: web.Request):
        socket = web.WebSocketResponse()
        await socket.prepare(req)

        rxq = Queue()
        txq = Queue()
        closed = False

        await self.socket_queue.put((rxq, txq))

        async def send():
            nonlocal closed

            while True:
                out_data = json.dumps(await txq.get())
                if closed:
                    break

                try:
                    await socket.send_str(out_data)
                except ConnectionResetError:
                    closed = True
                    await rxq.put(CLOSE_SIGNAL)
                    break

        async def receive():
            nonlocal closed

            while not closed:
                in_data = None
                try:
                    in_data = await socket.receive_str()
                except TypeError:
                    closed = True
                    await rxq.put(CLOSE_SIGNAL)
                    break

                await rxq.put(json.loads(in_data)['input'])

        await asyncio.gather(send(), receive())

        return socket

    async def start(self):        
        server = web.Application()
        server.add_routes((
            web.get('/', lambda req: self.get_index(req)),
            web.get('/index.js', lambda req: self.get_js(req)),
            web.get('/ws', lambda req: self.handle_socket(req))
        ))
        
        runner = web.AppRunner(server)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        print('serving http://localhost:%d'%self.port)

@io_sources.implementation('ws')
class WebSocketIOSource(IOSource):
    rxq: Queue
    txq: Queue
    
    def __init__(self, args):
        super().__init__(args)
        self.rxq = None
        self.txq = None

    async def bind(self):
        self.rxq, self.txq = (
            await WebSocketIOServer.next_socket(self.args)
        )

    async def unbind(self):
        pass

    def queue_write(self, data_type: str, data: dict = None):
        self.txq.put_nowait({
            'type': data_type,
            'data': data
        })

    async def read_input(
        self,
        message: str = None,
        signal_only: bool = False,
        options: list[str] = None,
        validator_fn: Callable[[str], Any] = None
    ) -> Any:
        if options:
            def validate(value):
                if not value in options:
                    raise ValueError()
                return value
            validator_fn = validate

        self.queue_write('input', {
            'message': message,
            'signal_only': signal_only,
            'options': options
        })

        value = None
        while True:
            value = await self.rxq.get()
            if value == CLOSE_SIGNAL:
                raise Exit()
            if validator_fn:
                try:
                    value = validator_fn(value)
                except ValueError:
                    self.queue_write('input_invalid')
                    continue
            break

        self.queue_write('input_ok')
        return value

    def write_message(self, message: str):
        self.queue_write('message', message)
    
    def write_timer(self, delay_seconds: int) -> Callable:
        self.queue_write('timer', delay_seconds)

        def stop():
            self.queue_write('unwrite_timer')
        return stop
    
    def write_event(self, event: Event, prefix: str):
        self.queue_write('event', {
            'prefix': prefix,
            'type': event.type,
            'exercise': event.exercise,
            'value': event.value
        })

    def write_exercise(self, exercise: Exercise, prefix: str):
        self.queue_write('exercise', {
            'prefix': prefix,
            'name': exercise.name,
            'type': exercise.type
        })

    def unwrite_messages(self, count: int):
        self.queue_write('unwrite_messages', count)
