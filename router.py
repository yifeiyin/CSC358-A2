from socketserver import UDPServer, BaseRequestHandler

PORT = 1111

class Router:
    def __init__(self, ip):
        self.ip = ip

    def start(self):
        self.server = UDPServer(server_address=(self.ip, PORT), RequestHandlerClass=Handler)
        self.server.serve_forever()


class Handler(BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        client_ip = self.client_address[0]

        print(f"{client_ip} wrote: {data}")
        socket.sendto(data.upper(), (client_ip, PORT))


if __name__ == '__main__':
    h = Router('localhost')
    h.start()
