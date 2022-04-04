#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI, makeTerms
from mininet.log import setLogLevel, info

def net1():
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    # h4 = net.addHost('h4', ip='10.0.0.4')

    info('*** Adding switch\n')
    # s7 = net.addSwitch('s7')
    s8 = net.addSwitch('s8')

    info('*** Creating links\n')
    net.addLink(h1, s8)
    net.addLink(h2, s8)
    net.addLink(h3, s8)
    # net.addLink(h4, s8)

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
    terms = makeTerms([h1,h2,h3])

    CLI(net)

    net.stopXterms()

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    net1()
