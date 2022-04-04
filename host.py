#!/usr/bin/python

from operator import ne
import socket
from socketserver import UDPServer, BaseRequestHandler
import subprocess
from sys import argv
import json
import logging

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# ff = logging.Formatter('%(funcName)-10s %(lineno)-3d: %(levelname)-8s %(message)s')
ff = logging.Formatter('@%(lineno)-3d: %(levelname)-8s %(message)s')
console.setFormatter(ff)
logging.getLogger('').addHandler(console)

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

PORT = 1111

def encode(data):
    return bytes(json.dumps(data), 'utf-8')

def decode(data):
    return json.loads(data.decode('utf-8'))

def send(neighbor, data):
    logger.debug(f'Sending through {neighbor}: {data}')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(encode(data), (neighbor, PORT))

def normalize_ip(ip):
    if ip.startswith('10.0.0.'):
        return ip
    return f'10.0.0.{ip}'

def my_ip():
    out = subprocess.run('ip addr | awk \'/inet 10/ { print $2 }\'', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout
    ip = out.strip()
    ip = ip.replace('/8', '')
    assert ip.startswith('10.0.0.')
    return ip


def find_neighbors():
    out = subprocess.run('ip neighbor', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout
    ips = []
    for line in out.strip().split('\n'):
        if line.startswith('10.0.0.') and '00:00:00:00:00:00' not in line:
            ips.append(line.split()[0])
    return ips


class Host:
    def __init__(self):
        self.neighbors = find_neighbors()

    def start_server(self):
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=Handler)
        logger.info('Starting client server')
        self.server.serve_forever()

    def broadcast(self, ttl=0):
        logger.debug('Broadcasting')
        for neighbor in self.neighbors:
            send(neighbor, { 'src':  my_ip(), 'dst': 'ALL', 'ttl': ttl })

class Router:
    def __init__(self):
        self.forwarding_table = {}
        assert Handler.router is None
        Handler.router = self

    def start_server(self):
        logger.info('Starting router server')
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=Handler)
        self.server.serve_forever()


class Handler(BaseRequestHandler):
    router = None

    def handle(self):
        data, socket = self.request
        data_len = len(data)
        client_ip = self.client_address[0]
        data = decode(data)
        logger.info(f"Received {data_len}b from {client_ip}: {data}")
        if self.router is None:
            return

        src = data['src']
        dst = data['dst']
        ttl = data['ttl']

        current_entry = self.router.forwarding_table.get(src, None)
        if current_entry is None:
            logger.debug(f'Adding new forwarding table entry: {src} is at {client_ip}')
            self.router.forwarding_table[src] = client_ip
        elif current_entry != client_ip:
            logger.fatal(f"Conflicting forwarding table entry {src} is at {current_entry}")
        else:
            logger.debug(f"{src} is already forwarded to {client_ip}")
            pass

        if ttl == 0:
            logger.warning(f'Dropping packet from {src} to {dst} due to TTL')
            return

        if dst == 'ALL':
            logger.debug(f'Broadcasting packet from {src} to {dst}')
            for neighbor in self.router.neighbors:
                send(neighbor, { 'src': src, 'dst': dst, 'ttl': ttl - 1 })

        if dst in self.router.forwarding_table:
            logger.debug(f'Forwarding packet from {src} to {dst}')
            send(self.router.forwarding_table[dst], { 'src': src, 'dst': dst, 'ttl': ttl - 1 })

        else:
            logger.warning(f'Dropping packet from {src} to {dst} due to no route')


if __name__ == '__main__':
    neighbors = find_neighbors()
    logger.debug(f'Found neighbors: {neighbors}')

    if len(argv) == 1:
        logger.error('Aviable commands: start, broadcast, send <ip> <data>')
        exit(1)

    if argv[1] == 'start' and len(neighbors) == 1:
        h = Host()
        h.start_server()

    elif argv[1] == 'start':
        h = Router()
        h.start_server()

    elif argv[1] == 'broadcast':
        if len(neighbors) != 1:
            logger.warning('Broadcasting despite neighbor count is not 1')
        h = Host()
        h.broadcast(ttl=int(argv[2]) if len(argv) > 2 else 0)

    elif argv[1] == 'send':
        if len(argv) <= 2:
            logger.error('send <neighbor> <dst> [ttl]')
            exit(1)
        through = normalize_ip(argv[2])
        dst = normalize_ip(argv[3])
        src = my_ip()
        ttl = int(argv[4]) if len(argv) > 4 else 5
        send(through, { 'src': src, 'dst': dst, 'ttl': ttl })

