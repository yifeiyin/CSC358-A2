import socket
from socketserver import TCPServer, BaseRequestHandler

PORT = 1111

class Host:
    def __init__(self, ip):
        self.ip = ip

    def start(self):
        self.server = TCPServer(server_address=('', PORT), RequestHandlerClass=Handler)
        self.server.serve_forever()

    def broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # sock.bind(('', 0))
        try:
            # sock.sendall(bytes('hello', 'utf-8'))
            # sock.connect(('', PORT))
            # sock.send(bytes('hello', 'utf-8'))
            # sock.close()
            # sock.sendto(bytes('hello', 'utf-8'), ('10.0.255.255', PORT))
            sock.sendto(bytes('hello', 'utf-8'), ('10.0.0.1', PORT))
# (b'hello', <socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0, laddr=('0.0.0.0', 1111)>)
# ('10.0.0.2', 38174) wrote: b'hello'

        except Exception as e:
            print(e)

class Handler(BaseRequestHandler):
    def handle(self):
        print(self.request)
        data, socket = self.request
        client_ip = self.client_address[0]

        print(f"{self.client_address} wrote: {data}")
        socket.sendto(data.upper(), (client_ip, PORT))


if __name__ == '__main__':
    h = Host('localhost')
    h.broadcast()
    h.start()
