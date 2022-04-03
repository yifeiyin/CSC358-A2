import socket
from socketserver import UDPServer, BaseRequestHandler
import subprocess

PORT = 1111


def send(dest, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(data, (dest, PORT))


class Host:
    def __init__(self):
        self.neighbors = self.find_neighbors()

    def find_neighbors(self):
        out = subprocess.run('ip neighbor', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout
        ips = [ line.split(' ')[0] for line in out.split('\n') if len(line) > 0 ]
        return ips

    def start_server(self):
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=Handler)
        self.server.serve_forever()
        print('test')

    def broadcast(self):
        for neighbor in self.neighbors:
            send(neighbor, b'Hello')


class Handler(BaseRequestHandler):
    def handle(self):
        print(self.request)
        data, socket = self.request
        client_ip = self.client_address[0]

        print(f"{self.client_address} wrote: {data}")
        socket.sendto(data.upper(), (client_ip, PORT))


if __name__ == '__main__':
    h = Host()
    h.broadcast()
    h.start_server()
