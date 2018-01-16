import asyncio
import re
import signal
import sys

__version__ = '0.1.0.dev1'


class Server(asyncio.Protocol):
    def __init__(self, timeout):
        self._loop = asyncio.get_event_loop()
        self._transport = None
        self._keepalive = None
        self._timeout = timeout
        self._timing = None

    def connection_made(self, transport):
        print('Connection made: ' + str(id(self)))
        self._transport = transport
        self._keepalive = True
        if self._timeout:
            self._timing = self._loop.call_later(self._timeout, self.on_timeout)

    def connection_lost(self, e):
        if e:
            print('Connection lost: ' + str(id(self)))
            print(e)
        else:
            print('Connection closed: ' + str(id(self)))

    def data_received(self, data):
        print('Received: ' + repr(data))
        # TODO: parse request
        self._transport.write('HTTP/1.1 200 OK\r\n'.encode('utf-8'))
        self._transport.write(('Server: MiniPyp/' + __version__ + '\r\n').encode('utf-8'))
        self._transport.write('Content-Type: text/html; charset=utf-8\r\n'.encode('utf-8'))
        self._transport.write('Content-Length: 13\r\n'.encode('utf-8'))
        self._transport.write('\r\n'.encode('utf-8'))
        self._transport.write('Hello, world!'.encode('utf-8'))
        if not self._keepalive:
            if self._timing:
                self._timing.cancel()
            self._transport.close()
        if self._timeout and self._timing:
            self._timing.cancel()
            self._timing = self._loop.call_later(self._timeout, self.on_timeout)

    def on_timeout(self):
        print('Connection timed out: ' + str(id(self)))
        self._transport.close()


class MiniPyP:
    def __init__(self, host="0.0.0.0", port=80, root='/var/www/html', timeout=15):
        self._host = host
        self._port = port
        self._root = root
        self._timeout = timeout
        self._sites = []
        self._handlers = {}
        self._clients = {}

    def start(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        if sys.platform == 'win32':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        coro = loop.create_server(lambda: Server(self._timeout), self._host, self._port)
        server = loop.run_until_complete(coro)
        sockname = server.sockets[0].getsockname()
        print('Starting MiniPyP server on ' + sockname[0] + ':' + str(sockname[1]))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self):
        print('Cleaning up...')

    def add_site(self, site):
        if not isinstance(site, Site):
            raise Exception('add_site failed: Site not provided')
        self._sites.append(site)

    def add_handler(self, filetype, handler):
        filetype = filetype.lower()
        if not isinstance(handler, Handler):
            raise Exception('add_handler failed: Handler not provided')
        if not re.match('/^[a-z]+$/', filetype):
            raise Exception('add_handler failed: invalid filetype')
        if filetype in self._handlers.keys():
            raise Exception('add_handler failed: handler already exists for .' + filetype)
        self._handlers[filetype] = handler


class Site:
    def __init__(self, hosts, root):
        self._hosts = hosts
        self._root = root


class ProxySite(Site):
    def __init__(self, hosts, proxy):
        super().__init__(hosts, None)
        self._proxy = proxy


class Handler:
    def __init__(self, name):
        self._name = name

    def handle(self):
        raise Exception('Handler requires handle()')
