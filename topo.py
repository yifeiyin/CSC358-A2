#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def net1():
    net = Mininet(controller=Controller, waitConnected=True, autoSetMacs=True, autoStaticArp=True)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')

    info('*** Adding switch\n')
    s3 = net.addSwitch('s3')

    info('*** Creating links\n')
    net.addLink(h1, s3)
    net.addLink(h2, s3)

    info('*** Starting network\n')
    net.start()

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    net1()
