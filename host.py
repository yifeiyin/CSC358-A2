from socketserver import UDPServer, BaseRequestHandler

class Host:
    def __init__(self, ip, next_hop):
        self.ip = ip
        self.next_hop = next_hop

    def start(self):
        self.server = UDPServer(server_address=(self.ip, 1111), RequestHandlerClass=Handler)
        self.server.serve_forever()

    # def send(self, dest, msg):
    #     pass

    # def receive(self):
    #     pass

class Handler(BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        socket.sendto(data.upper(), self.client_address)


if __name__ == '__main__':
    h = Host('localhost', '')
    h.start()
