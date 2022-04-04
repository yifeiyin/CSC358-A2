#!/usr/bin/python
# c-spell: ignore ospf inet dgram sendto

import socket
from socketserver import UDPServer, BaseRequestHandler
import subprocess
from sys import argv
import json
import logging
from log_helper import ColorLogFormatter
from algo import ospf_algo, rip_new_table

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(ColorLogFormatter())
logging.getLogger('').addHandler(console)

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)

PORT = 1111

monitor_ip = '10.0.0.255'

def encode(data):
    return bytes(json.dumps(data), 'utf-8')

def decode(data):
    return json.loads(data.decode('utf-8'))

def send(neighbor, data):
    logger.debug(f'Sending through {neighbor}: {data}')
    if neighbor not in neighbors and neighbor != monitor_ip:
        logger.critical(f'{neighbor} is not a neighbor')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(encode(data), (neighbor, PORT))

def normalize_ip(ip):
    if ip.startswith('10.0.0.'):
        return ip
    return f'10.0.0.{ip}'


def get_my_ip():
    out = subprocess.run('ip addr | awk \'/inet 10/ { print $2 }\'', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout
    ip = out.strip()
    ip = ip.replace('/8', '')
    assert ip.startswith('10.0.0.')
    return ip
my_ip = get_my_ip()

def get_neighbors():
    out = subprocess.run('ip neighbor', shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout
    ips = []
    for line in out.strip().split('\n'):
        if line.startswith('10.0.0.') and '00:00:00:00:00:00' not in line:
            ip = line.split()[0]
            if ip.endswith('255'): # skip monitor node
                continue
            ips.append(ip)
    return ips
neighbors = get_neighbors()


class Host:
    def __init__(self):
        self.neighbors = neighbors

    def start_server(self):
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=HostHandler)
        logger.info('Starting client server')
        self.server.serve_forever()

    def broadcast(self, ttl=0):
        logger.debug(f'Broadcasting with {ttl=}')
        for neighbor in self.neighbors:
            send(neighbor, { 'src': my_ip, 'dst': 'ALL', 'ttl': ttl })


class HostHandler(BaseRequestHandler):
    def handle(self):
        data, = self.request
        data_len = len(data)
        client_ip = self.client_address[0]
        data = decode(data)
        logger.info(f"Received {data_len}b from {client_ip}: {data}")

        src = data['src']
        dst = data['dst']
        ttl = data['ttl']

        if dst == my_ip:
            logger.info(f'Received packet FOR ME from {src}! Dropping.')
            return
        else:
            logger.error(f'Unexpected packet from {src}: {data=}')
            return



class Router:
    def __init__(self):
        self.forwarding_table = {}
        self.rip_mode = False
        assert RouterHandler.router is None
        RouterHandler.router = self

    def start_server(self):
        logger.info('Starting router server')
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=RouterHandler)
        self.server.serve_forever()

    def broadcast(self, ttl=0):
        logger.debug(f'Broadcasting with {ttl=}')
        for neighbor in self.neighbors:
            send(neighbor, { 'src': my_ip, 'dst': 'ALL', 'ttl': ttl })

    def broadcast_for_rip(self):
        logger.debug(f'Broadcasting forwarding table')
        for neighbor in self.neighbors:
            send(neighbor, { 'rip-update': self.forwarding_table, 'src': my_ip, 'dst': neighbor })


class RouterHandler(BaseRequestHandler):
    router = None
    def handle_monitor_request(self, data):
        request = data['request']
        if request == 'rip':
            logger.info('Activating RIP mode')
            self.router.rip_mode = True
        elif request == 'get-table':
            logger.debug(f'Sending forwarding table')
            # sleep(0.1 * int(my_ip[-1]))
            send(monitor_ip, { 'table': self.router.forwarding_table })
        elif request == 'print-table':
            from pprint import pprint
            logger.info(f'Here is the current forwarding table as requested:')
            pprint(self.router.forwarding_table)
        elif request == 'set-table':
            logger.info(f'Setting table to {data["table"]}')
            assert data['table'] is not None
            self.router.forwarding_table = data['table']
        else:
            logger.error(f'Unknown request: {request}')

    def handle(self):
        data, = self.request
        data_len = len(data)
        client_ip = self.client_address[0]
        data = decode(data)
        logger.info(f"Received {data_len}b from {client_ip}")

        assert self.router is not None

        if data.get('request') is not None:
            logger.debug('It was a forwarding table request')
            self.handle_monitor_request(data)
            return

        if data.get('rip-update') is not None:
            logger.debug('It was a rip update message')
            if data['dst'] != my_ip:
                logger.critical(f'Unexpected rip update message, intended for {data["dst"]} but I am {my_ip}')
            new_table = rip_new_table(self.router.forwarding_table, data['rip-update'], src=data['src'])
            if new_table is not None:
                self.router.forwarding_table = new_table
                self.router.broadcast_for_rip()
            return

        logger.debug('It was a routing request')
        src = data['src']
        dst = data['dst']
        ttl = data['ttl']

        if dst == my_ip:
            logger.error(f'Unexpected packet for router from {src}. Dropping.')
            return

        forwarding_table_changed = False

        current_entry = self.router.forwarding_table.get(src, None)
        if current_entry is None:
            logger.debug(f'Adding new forwarding table entry: {src} is at {client_ip}')
            self.router.forwarding_table[src] = (client_ip, 1)
            forwarding_table_changed = True
        elif current_entry[0] != client_ip:
            logger.error(f"Conflicting forwarding table: got {src} from {client_ip}, previously at {current_entry}")
        else:
            logger.debug(f"{src} is already forwarded to {client_ip}")
            pass

        if ttl == 0:
            logger.warning(f'Dropping packet from {src} to {dst} due to TTL')

        elif dst == 'ALL':
            logger.debug(f'Broadcasting packet from {src} to {dst}')
            for neighbor in self.router.neighbors:
                if neighbor == client_ip: continue # Don't send it to source
                send(neighbor, { 'src': src, 'dst': dst, 'ttl': ttl - 1 })

        elif dst in self.router.forwarding_table:
            logger.debug(f'Forwarding packet from {src} to {dst}')
            send(self.router.forwarding_table[dst][0], { 'src': src, 'dst': dst, 'ttl': ttl - 1 })

        else:
            logger.warning(f'Dropping packet from {src} to {dst} due to no route')

        if forwarding_table_changed and self.router.rip_mode:
            logger.debug(f'Sending RIP update')
            self.router.broadcast_for_rip()


class Monitor:
    def __init__(self):
        self.table_received = None
        assert MonitorHandler.monitor is None
        MonitorHandler.monitor = self

    def request_update(self):
        for neighbor in neighbors:
            send(neighbor, { 'request': 'get-table' })

    def print_table(self, router_ip):
        send(router_ip, { 'request': 'print-table' })

    def print_all_table(self):
        for neighbor in neighbors:
            send(neighbor, { 'request': 'print-table' })

    def start_server(self):
        logger.info('Starting monitor server')
        self.server = UDPServer(server_address=('', PORT), RequestHandlerClass=MonitorHandler)
        self.server.serve_forever()


class MonitorHandler(BaseRequestHandler):
    monitor: Monitor = None

    def handle(self):
        data, = self.request
        client_ip = self.client_address[0]
        data = decode(data)
        logger.info(f"Received routing table from {client_ip}")

        assert self.monitor is not None

        if self.monitor.table_received is None:
            logger.info(f'Starting new routing table update process')
            self.monitor.table_received = { client_ip: data['table'] }
        else:
            self.monitor.table_received[client_ip] = data['table']

        not_received = [neighbor for neighbor in neighbors if neighbor not in self.monitor.table_received]
        if len(not_received) == 0:
            logger.debug(f'Calculating new routing table')
            tables_to_send = ospf_algo(self.monitor.table_received)
            self.monitor.table_received = None
            for neighbor in neighbors:
                send(neighbor, { 'request': 'set-table', 'table': tables_to_send[neighbor] })
            return
        else:
            logger.debug(f'Still waiting response from {not_received}')



if __name__ == '__main__':
    logger.debug(f'Found neighbors: {neighbors}')

    # logger.debug('Hello')
    # logger.info('Hello')
    # logger.warning('Hello')
    # logger.error('Hello')
    # logger.critical('Hello')


    if len(argv) == 1:
        logger.error('Available commands: start, broadcast, send, get')
        exit(1)

    if argv[1] == 'start' and len(neighbors) == 1:
        h = Host()
        h.broadcast()
        h.start_server()

    elif argv[1] == 'start' and my_ip.endswith('255'):
        h = Monitor()
        h.start_server()

    elif argv[1] == 'start':
        h = Router()
        h.broadcast()
        h.start_server()

    elif argv[1] == 'broadcast':
        print(argv)
        if len(neighbors) != 1:
            logger.warning('Broadcasting despite neighbor count is not 1')
        h = Host()
        h.broadcast(ttl=int(argv[2]) if len(argv) > 2 else 0)

    elif argv[1] == 'send':
        if len(argv) <= 2:
            logger.error('send <dst> [ttl]')
            exit(1)
        assert len(neighbors) == 1
        through = neighbors[0]
        dst = normalize_ip(argv[2])
        src = my_ip
        ttl = int(argv[3]) if len(argv) > 4 else 5
        send(through, { 'src': src, 'dst': dst, 'ttl': ttl })

    elif argv[1] == 'get':
        if len(argv) <= 2:
            logger.error('get <router | all>')
            exit(1)
        m = Monitor()
        if argv[2] == 'all':
            m.print_all_table()
        else:
            m.print_table(normalize_ip(argv[2]))

    elif argv[1] == 'update':
        m = Monitor()
        m.request_update()
