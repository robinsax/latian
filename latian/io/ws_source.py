import io
import json
import asyncio
from aiohttp import web
from asyncio import Queue
from typing import Callable, Any, Coroutine

from ..model import Event
from ..common import Exit
from .source import IOSource, io_sources

FRONTEND_ASSET = 'latian/io/ws_source.html'
CLOSE_SIGNAL = '<<close>>'

async def create_server(
    port: int, in_queue: Queue, out_queue: Queue
) -> Callable[[], Coroutine]:
    index_html = None
    with io.open(FRONTEND_ASSET, encoding='utf-8') as asset_io:
       index_html = asset_io.read()
    
    index_html = index_html.replace('$PORT', str(port))

    server = web.Application()

    async def get_index(req):
        return web.Response(
            text=index_html,
            content_type='text/html'
        )
    
    async def handle_socket(req):
        socket = web.WebSocketResponse()
        await socket.prepare(req)

        async def send():
            while True:
                out_data = await out_queue.get()
                print('send %s'%out_data)

                try:
                    await socket.send_str(out_data)
                except ConnectionResetError:
                    print('client disconnect')
                    await in_queue.put(CLOSE_SIGNAL)
                    break

        async def recieve():
            while True:
                in_data = None
                try:
                    in_data = await socket.receive_str()
                except TypeError:
                    await in_queue.put(CLOSE_SIGNAL)
                    break

                print('recv %s'%in_data)
                await in_queue.put(json.loads(in_data)['input'])

        await asyncio.gather(send(), recieve())

        return socket

    server.add_routes((
        web.get('/', get_index),
        web.get('/ws', handle_socket)
    ))
    
    runner = web.AppRunner(server)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print('serving http://localhost:%d'%port)

    async def stop():
        await site.stop()
        await runner.cleanup()
        print('server off')
    return stop

@io_sources.implementation('ws')
class WebSocketIOSource(IOSource):
    stop_server: Callable[[], Coroutine] = False
    in_queue: Queue = None
    out_queue: Queue = None
    
    def __init__(self, cli_args):
        super().__init__(cli_args)
        self.stop_server = False
        self.in_queue = Queue()
        self.out_queue = Queue()

    async def bind(self):
        self.stop_server = await create_server(
            self.cli_args.get('port'), self.in_queue, self.out_queue
        )

    async def unbind(self):
        await self.stop_server()

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
        if message:
            message = 'pick %s'%message
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
            'mode': event.mode,
            'exercise': event.exercise,
            'value': event.value
        })

    def unwrite_messages(self, count: int):
        self._push_out('unwrite_messages', count)
