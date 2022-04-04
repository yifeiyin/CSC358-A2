#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI, makeTerms
from mininet.log import setLogLevel, info

def net1():
    """
    h1 <-> h2 (router) <-> h3
    """
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')

    info('*** Adding switch\n')
    s8 = net.addSwitch('s8')

    info('*** Creating links\n')
    net.addLink(h1, s8)
    net.addLink(h2, s8)
    net.addLink(h3, s8)

    info('*** Starting network\n')
    net.start()

    info('*** Setting up arp entries\n')
    h1.setARP(ip=h2.IP(), mac=h2.MAC())
    h1.setARP(ip=h3.IP(), mac='00:00:00:00:00:00')
    # h2.setARP(ip=h1.IP(), mac=h1.MAC())
    # h2.setARP(ip=h3.IP(), mac=h3.MAC())
    h3.setARP(ip=h2.IP(), mac=h2.MAC())
    h3.setARP(ip=h1.IP(), mac='00:00:00:00:00:00')

    info('*** Running CLI\n')
    makeTerms([h1,h2,h3])

    CLI(net)

    net.stopXterms()

    info('*** Stopping network')
    net.stop()


def connect(a, b):
    a.setARP(ip=b.IP(), mac=b.MAC())
    b.setARP(ip=a.IP(), mac=a.MAC())

def disconnect(a, b):
    a.setARP(ip=b.IP(), mac='00:00:00:00:00:00')
    b.setARP(ip=a.IP(), mac='00:00:00:00:00:00')

def net2():
    """
    h1 <->
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


    info('*** Running CLI\n')
    makeTerms(all_hosts)

    CLI(net)

    net.stopXterms()

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    net2()
