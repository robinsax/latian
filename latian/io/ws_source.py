'''
I/O source implementation using a websocket server and associated
frontend.

Transacts JSON Websocket messages.
'''
import io
import json
import asyncio
from aiohttp import web
from asyncio import Queue
from typing import Callable, Any, Coroutine

from ..cli import CLIArgs
from ..model import Event
from ..common import Exit
from .io_source import IOSource, io_sources

FRONTEND_ASSET = 'latian/io/ws_source.html'
CLOSE_SIGNAL = '<<close>>'

def _load_index() -> str:
    with io.open(FRONTEND_ASSET, encoding='utf-8') as asset_io:
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

    async def index(self, req: web.Request):
        return web.Response(
            text=_load_index().replace('$PORT', str(self.port)),
            content_type='text/html'
        )
    
    async def socket(self, req: web.Request):
        socket = web.WebSocketResponse()
        await socket.prepare(req)

        in_queue = Queue()
        out_queue = Queue()
        closed = False
        print('client available')
        await self.socket_queue.put((in_queue, out_queue))

        async def send():
            nonlocal closed

            while True:
                out_data = await out_queue.get()
                if closed:
                    return
                print('send %s'%out_data)

                try:
                    await socket.send_str(out_data)
                except ConnectionResetError:
                    closed = True
                    await in_queue.put(CLOSE_SIGNAL)
                    break

        async def receive():
            nonlocal closed

            while not closed:
                in_data = None
                try:
                    in_data = await socket.receive_str()
                except TypeError:
                    closed = True
                    await in_queue.put(CLOSE_SIGNAL)
                    break

                print('recv %s'%in_data)
                await in_queue.put(json.loads(in_data)['input'])

        await asyncio.gather(send(), receive())

        return socket

    async def start(self):        
        server = web.Application()
        server.add_routes((
            web.get('/', lambda req: self.index(req)),
            web.get('/ws', lambda req: self.socket(req))
        ))
        
        runner = web.AppRunner(server)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        print('serving http://localhost:%d'%self.port)

@io_sources.implementation('ws')
class WebSocketIOSource(IOSource):
    stop_server: Callable[[], Coroutine]
    in_queue: Queue
    out_queue: Queue
    
    def __init__(self, args):
        super().__init__(args)
        self.stop_server = None
        self.in_queue = None
        self.out_queue = None

    async def bind(self):
        self.in_queue, self.out_queue = (
            await WebSocketIOServer.next_socket(self.args)
        )
        print('io source bound')

    async def unbind(self):
        pass

    def _push_out(self, data_type: str, data: dict = None):
        raw_out = json.dumps({
            'type': data_type,
            'data': data
        })
        self.out_queue.put_nowait(raw_out)

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

        self._push_out('input', {
            'message': message,
            'signal_only': signal_only,
            'options': options
        })

        value = None
        while True:
            value = await self.in_queue.get()
            if value == CLOSE_SIGNAL:
                print('client disconnect')
                raise Exit()
            if validator_fn:
                try:
                    value = validator_fn(value)
                except ValueError:
                    self._push_out('input_invalid')
                    continue
            break

        self._push_out('input_ok')
        return value

    def write_message(self, message: str):
        self._push_out('message', message)
    
    def write_timer(self, delay_seconds: int) -> Callable:
        self._push_out('timer', delay_seconds)

        def stop():
            self._push_out('unwrite_timer')
        return stop
    
    def write_event(self, event: Event, prefix: str):
        self._push_out('event', {
            'prefix': prefix,
            'type': event.type,
            'exercise': event.exercise,
            'value': event.value
        })

    def unwrite_messages(self, count: int):
        self._push_out('unwrite_messages', count)
