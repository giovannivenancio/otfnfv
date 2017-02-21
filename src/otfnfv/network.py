#!/usr/bin/env python

import os
import time
from functools     import partial
from mininet.net   import Mininet
from mininet.cli   import CLI
from mininet.clean import cleanup
from mininet.topo  import Topo
from mininet.node  import Host, OVSSwitch, Ryu
from topology      import create_topology
from utils         import *
from mininet.util  import waitListening

class MininetNetwork():

    def __init__(self):
        self.conn, self.db = connect(None)

        self.vnf = self.db['vnf']
        self.control = self.db['control']

    def create_network(self):
        """
        Create topology, Ryu controller and build the network
        """

        # Cleanup old sessions before build a new one
        cleanup()

        # Create Topology
        topo = create_topology()

        # Set switch to use OpenFlow13
        OVSSwitch13 = partial(OVSSwitch, protocols='OpenFlow13')

        # Create Ryu Controller
        ryu = Ryu('ryu', RYU_APP_PATH, port=RYU_PORT)

        # Create Mininet
        net = Mininet(
            topo=topo,
            switch=OVSSwitch13,
            controller=ryu,
            autoSetMacs=True
        )

        return net

    def get_switch_pids(self, net):
        """
        Get all switch pids
        """

        pids = []

        s1 = net.get('s1')
        pids.append({'id': 's1', 'pid': s1.__dict__['pid']})

        s2 = net.get('s2')
        pids.append({'id': 's2', 'pid': s2.__dict__['pid']})

        s3 = net.get('s3')
        pids.append({'id': 's2', 'pid': s3.__dict__['pid']})

        self.control.find_one_and_update({}, {
            '$set' : { 'network.switch': pids }
        })

    def instance(self, host, script_dir, vnf_name):
        """
        Instance a new script
        script_dir is the dir that script is located from src/
        script is the name of the file
        """

        vnf_instance = self.vnf.find_one({'_id': vnf_name})

        if not vnf_instance:
            return "Script not found!"

        script = vnf_instance['script']

        if vnf_name == 'filter':
            perf = ' > /var/log/otfnfv/perf.log'
            log_path = ' 2> /var/log/otfnfv/filter.log'
            cmd = PATH + script_dir + script + perf + log_path + ' &'
        else:
            log_path = ' 2> /var/log/otfnfv/%s.log' % vnf_name.lower()
            cmd = PATH + script_dir + script + log_path + ' &'

        host.cmd(cmd)

        # Used to 'trick' the code and allow
        # undeveloped VNFs to be shown on interface
        if vnf_name != 'Statistics':
            return

        socket_file = '/var/run/%s_socket' % vnf_name.lower()

        execute(['touch', socket_file])

        if vnf_name != 'filter':
            # Set flag to create new connection
            self.control.find_one_and_update({}, {
                '$set' : { 'vnf.create_connection': vnf_name }
            })

    def kill(self, host, vnf_name):
        """
        Kill a VNF
        """

        script = self.vnf.find_one({'_id': vnf_name})['script']

        cmd = 'pkill -f %s' % script

        return host.cmd(cmd)

if __name__ == '__main__':
    mn = MininetNetwork()

    # Build network
    net = mn.create_network()

    # Allow mininet to connect with external internet and start it
    net.addNAT().configDefault()
    net.start()

    # Get hosts
    vnf_filter = net.get('filter')
    vnf_filter.cmd('/usr/sbin/sshd -D &')

    services = net.get('services')
    services.cmd('/usr/sbin/sshd -D &')

    # Get Host 1 and Run SSH daemon
    h1 = net.get('h1')
    h1.cmd('/usr/sbin/sshd -D &')

    # Get Host 2 and Run SSH daemon
    h2 = net.get('h2')
    h2.cmd('/usr/sbin/sshd -D &')

    # Inform interface controller about switch pids
    mn.get_switch_pids(net)

    # Enable Mininet Command-line Interface
    #CLI(net)

    # Start NFV
    mn.instance(vnf_filter, 'otfnfv/', 'filter')

    vnf_status = mn.control.find_one({}, {'vnf' : 1})['vnf']

    while not mn.control.find_one({}, {'network': 1})['network']['stop']:
        vnf_status = mn.control.find_one({}, {'vnf' : 1})['vnf']

        # Network has VNF to instantiate/kill
        if vnf_status['working']:
            vnf_name = vnf_status['to_instantiate']
            vnf_kill = vnf_status['to_kill']

            if vnf_name != '':
                mn.instance(services, 'vnf/', vnf_name)
                lst = 'vnf.to_instantiate'
            else:
                mn.kill(services, vnf_kill)
                lst = 'vnf.to_kill'

            mn.control.find_one_and_update({}, {
                '$set': {
                    lst: '',
                    'vnf.working': False
                },
            })

        time.sleep(2)

    mn.control.find_one_and_update({}, {
        '$set': { 'network.stop': False }
    })

    # Close MongoDB connection
    mn.conn.close()

    # Stop Mininet
    net.stop()
