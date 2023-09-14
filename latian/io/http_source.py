import json
from time import sleep
from threading import Thread
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from ..common import Exit
from .source import IOSource, io_sources    

def make_handler(in_queue: list[str], out_queue: list[str]):
    index_html = None
    with open('latian/pub/index.html', 'rb') as index_io:
        index_html = index_io.read()

    class Handler(SimpleHTTPRequestHandler):

        def _respond(self, status: int, mime: str, data: bytes):
            self.send_response(status)
            self.send_header('content-type', mime)
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == '/':
                self._respond(200, 'text/html', index_html)
            elif self.path == '/favicon.ico':
                self._respond(404, 'text/plain', b'')
            else:
                self.send_response(200)
                self.send_header('content-type', 'text/json')
                self.end_headers()

                while not len(out_queue):
                    sleep(0.25)
                out_data = json.dumps(out_queue).encode('utf-8')
                out_queue.clear()

                self.wfile.write(out_data)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            in_data = self.rfile.read(content_length).decode('utf-8')

            in_queue.extend(json.loads(in_data))

            self._respond(200, 'text/json', b'{"ok": true}')

    return Handler

@io_sources.implementation('http')
class HttpIOSource(IOSource):
    serving: bool = False
    server: ThreadingHTTPServer = None
    in_queue: list[str] = None
    out_queue: list[str] = None
    
    def __init__(self, cli_args):
        super().__init__(cli_args)
        self.serving = False
        self.server = None
        self.in_queue = list()
        self.out_queue = list()

    def _serve(self):
        port = self.cli_args.get('port')
        Handler = make_handler(self.in_queue, self.out_queue)

        self.server = ThreadingHTTPServer(('0.0.0.0', port), Handler)
        self.serving = True

        print('serving on :%d'%port)

        while self.serving:
            self.server.handle_request()
        print('server off')

    def bind(self):
        def serve():
            self._serve()

        self.server = Thread(target=serve)
        self.server.start()

    def unbind(self):
        self.serving = False

    def read_blocking(self):
        try:
            while not len(self.in_queue):
                sleep(0.1)
        except KeyboardInterrupt:
            raise Exit()

        return self.in_queue.pop(0)

    def write(self, string: str, formats: tuple() = None):
        if formats:
            string = string%formats

        self.out_queue.append(string)

    def unwrite_lines(self, count: int):
        self.out_queue.append('@unwrite:%d'%count)
