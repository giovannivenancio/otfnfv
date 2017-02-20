#!/usr/bin/env python

"""

Custom Topology

"""

from mininet.topo import Topo

class network_topology( Topo ):

    def __init__(self):
        Topo.__init__(self)

        # Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Filter
        vnf = self.addHost('filter')

        # Services Host
        services = self.addHost('services')

        # Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(services, s1)
        self.addLink(vnf, s1)

def create_topology():
    return network_topology()

