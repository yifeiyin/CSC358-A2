#!/usr/bin/env python

from sys import argv
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI, makeTerms
from mininet.log import setLogLevel, info


def connect(a, b):
    a.setARP(ip=b.IP(), mac=b.MAC())
    b.setARP(ip=a.IP(), mac=a.MAC())

def disconnect(a, b):
    a.setARP(ip=b.IP(), mac='00:00:00:00:00:00')
    b.setARP(ip=a.IP(), mac='00:00:00:00:00:00')



def net1():
    """
    h1 <-> h2 (router) <-> h3
    """
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True)
    net.addController('c0')
    s99 = net.addSwitch('s99')

    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    hs = [h1, h2]
    r1 = net.addHost('r1', ip='10.0.0.101')
    rs = [r1]
    monitor = net.addHost('monitor', ip='10.0.0.255')
    all_hosts = [*hs, *rs, monitor]

    for x in all_hosts:
        net.addLink(x, s99)

    info('*** Starting network\n')
    net.start()

    info('*** Setting up arp entries\n')
    for i in range(len(all_hosts)):
        for j in range(i + 1, len(all_hosts)):
            disconnect(all_hosts[i], all_hosts[j])

    connect(h1, r1)
    connect(r1, h2)

    for r in rs:
        connect(r, monitor)

    makeTerms(all_hosts)
    CLI(net)
    net.stopXterms()
    net.stop()




def net2():
    """
           h1
           ^
           |
           v
    h2 <-> r1 <-> r2 <-> h3
    """
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True)
    net.addController('c0')
    s99 = net.addSwitch('s99')

    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    hs = [h1, h2, h3]
    r1 = net.addHost('r1', ip='10.0.0.101')
    r2 = net.addHost('r2', ip='10.0.0.102')
    rs = [r1, r2]
    monitor = net.addHost('monitor', ip='10.0.0.255')
    all_hosts = [*hs, *rs, monitor]

    for x in all_hosts:
        net.addLink(x, s99)

    info('*** Starting network\n')
    net.start()

    info('*** Setting up arp entries\n')
    for i in range(len(all_hosts)):
        for j in range(i + 1, len(all_hosts)):
            disconnect(all_hosts[i], all_hosts[j])

    connect(h1, r1)
    connect(h2, r1)
    connect(r1, r2)
    connect(r2, h3)

    for r in rs:
        connect(r, monitor)

    makeTerms(all_hosts)
    CLI(net)
    net.stopXterms()
    net.stop()



def net3():
    """
    Graph: https://imgur.com/a/EPzZZGJ
    """
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True)
    net.addController('c0')
    s99 = net.addSwitch('s99')

    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')
    h5 = net.addHost('h5', ip='10.0.0.5')
    h6 = net.addHost('h6', ip='10.0.0.6')
    hs = [h1, h2, h3, h4, h5, h6]
    r1 = net.addHost('r1', ip='10.0.0.101')
    r2 = net.addHost('r2', ip='10.0.0.102')
    r3 = net.addHost('r3', ip='10.0.0.103')
    r4 = net.addHost('r4', ip='10.0.0.104')
    r5 = net.addHost('r5', ip='10.0.0.105')
    r6 = net.addHost('r6', ip='10.0.0.106')
    r7 = net.addHost('r7', ip='10.0.0.107')
    r8 = net.addHost('r8', ip='10.0.0.108')
    r9 = net.addHost('r9', ip='10.0.0.109')
    r10 = net.addHost('r10', ip='10.0.0.110')
    r11 = net.addHost('r11', ip='10.0.0.111')
    r12 = net.addHost('r12', ip='10.0.0.112')
    rs = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12]
    monitor = net.addHost('monitor', ip='10.0.0.255')
    all_hosts = [*hs, *rs, monitor]

    for x in all_hosts:
        net.addLink(x, s99)

    info('*** Starting network\n')
    net.start()

    info('*** Setting up arp entries\n')
    for i in range(len(all_hosts)):
        for j in range(i + 1, len(all_hosts)):
            disconnect(all_hosts[i], all_hosts[j])

    connect(h1, r1)
    connect(r2, r1)
    connect(r2, h6)
    connect(r1, r3)
    connect(r3, r10)
    connect(r9, r10)
    connect(r9, r2)

    connect(r3, r4)
    connect(r4, r5)
    connect(r6, r5)
    connect(r6, r7)
    connect(r7, r8)
    connect(r9, r8)

    connect(r7, h5)
    connect(r6, h4)

    connect(r5, h2)
    connect(r5, r11)
    connect(r6, r11)

    connect(r12, r11)
    connect(r12, h3)


    for r in rs:
        connect(r, monitor)

    makeTerms(all_hosts)
    CLI(net)
    net.stopXterms()
    net.stop()



if __name__ == '__main__':
    setLogLevel('info')
    if len(argv) < 2:
        print(f'Usage: sudo python topo.py [1|2|3]')
        exit(1)

    [net1, net2, net3][int(argv[1]) - 1]()

