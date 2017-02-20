#!/usr/bin/env python

import time
import socket
from multiprocessing import Process, Queue
from scapy.all       import *
from utils           import *

import sys
import time
import datetime
import threading

class VNFFilter():

    def __init__(self):
        self.conn, self.db = connect('remote')

        # Rules collection
        self.coll_rules = self.db['rules']
        self.coll_filters = self.db['filters']
        self.coll_vnf = self.db['vnf']
        self.control = self.db['control']

        self.vnf_connections = {}
        self.rules = []

    def update_rules(self):
        """
        Update rules
        """

        self.rules = [doc for doc in self.coll_rules.find()]

        vnf_to_connect = Filter.update_connections()
        if vnf_to_connect:
            Filter.create_connection(vnf_to_connect)

    def update_connections(self):
        """
        Get vnf name to create connection
        """

        return self.control.find_one({}, {'vnf.create_connection': 1})['vnf']['create_connection']

    def create_connection(self, vnf):
        """
        Create a new connection
        """

        socket_file = '/var/run/%s_socket' % vnf.lower()

        port = self.coll_vnf.find_one({'_id': vnf}, {'port': 1})['port']

        time.sleep(1)

        self.vnf_connections[vnf] = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.vnf_connections[vnf].connect(socket_file)

        self.control.find_one_and_update({}, {
            '$set' : { 'vnf.create_connection': '' }
        })

    def process_packet(self, pkt):
        """
        Process the packet
        """

        pkt['rules'] = []

        # VNFs that should receive this packet
        vnfs = set()

        # Find rules that match this packet
        for rule in self.rules:
            for attr, value in rule.iteritems():
                if attr != 'vnf' and attr != '_id':
                    if attr == 'Protocol':
                        if value != 'Any':
                            if value.upper() not in pkt['Protocol']:
                                break
                    elif value != pkt[attr]:
                        break
            else:
                pkt['rules'].append(int(rule['_id']))
                vnfs.add(rule['vnf'])

        # Send packets to VNF's
        for vnf in vnfs:
            if vnf in self.vnf_connections:
                to_send = str(pkt)

                # Get number of chars to read on vnf, so it know
                # how to get packet by packet
                size = str(len(str(pkt)))

                if len(size) == 2:
                    size = '0' + size
                print "SENDING..."
                self.vnf_connections[vnf].send(size + to_send)

class Sniffer():

    def __init__(self):
        self.protocols = Filter.coll_filters.find_one(
           {'_id': 'Protocol'},
           {'options': 1})['options']

        self.protocols = [s.upper() for s in self.protocols]

    def get_layers(self, pkt):
        """
        Lists all layers of a packet
        """

        yield pkt.name

        while pkt.payload:
            pkt = pkt.payload
            yield pkt.name

    def parse_packet(self, pkt):
        """
        Parse sniffed packet
        """

        packet = {}

        if pkt.haslayer('Ether') or pkt.haslayer('Dot3'):
            if pkt.haslayer('ARP'):
                packet['Source IP'] = pkt['ARP'].psrc
                packet['Destination IP'] = pkt['ARP'].pdst
            elif pkt.haslayer('IP'):
                packet['Source IP'] = pkt['IP'].src
                packet['Destination IP'] = pkt['IP'].dst

                if pkt.haslayer('TCP'):
                    packet['Source Port'] = pkt['IP']['TCP'].sport
                    packet['Destination Port'] = pkt['IP']['TCP'].dport
                elif pkt.haslayer('UDP'):
                    packet['Source Port'] = pkt['IP']['UDP'].sport
                    packet['Destination Port'] = pkt['IP']['UDP'].dport
            elif pkt.haslayer('IPv6'):
                packet['Source IP'] = pkt['IPv6'].src
                packet['Destination IP'] = pkt['IPv6'].dst

        return packet

    def get_packet_protocols(self, pkt):
        """
        Based on layers, get packet type
        """

        layers = list(self.get_layers(pkt))
        layers = [s.upper() for s in layers]

        pkt_protocols = []

        for layer in layers:
            if layer.upper() in self.protocols:
                pkt_protocols.append(layer)
            else:
                break

        # Exceptions
        if pkt_protocols == []:
            pkt_protocols = ['Other']
        elif pkt_protocols == ['802.3']:
            pkt_protocols = ['Ethernet']

        return pkt_protocols

    def prepare_packet(self, pkt):
        """
        Parse packet and tag protocols
        """

        parsed_packet = self.parse_packet(pkt)
        parsed_packet['Protocol'] = self.get_packet_protocols(pkt)
        parsed_packet['Size'] = len(pkt)

        # When using filter on scapy sniffer, doesn't need to check source
        # of packets to discard them
        # Discard packets from Filter, Services and Local machine (which runs MongoDB)
        # if parsed_packet['Source IP'] in ['10.0.0.1', '10.0.0.4', '192.168.0.10']:
        #    return

        self.queue.put(parsed_packet)

    def sniff_packets(self):
        """
        Sniff packets and sent them to parent process
        """

        sniff(iface=INTERFACE, prn=self.prepare_packet, store=0, filter="udp")

Filter = VNFFilter()
sniffer = Sniffer()

# Create pipe to communicate with sniffer process
queue = Queue()

Filter.queue = queue
sniffer.queue = queue

# Create another process to sniff packets
sniffing = Process(target = sniffer.sniff_packets)
sniffing.start()

global count
global total_bytes
count = 0
total_bytes = 0

while True:
    Filter.update_rules()
    pkt = Filter.queue.get()
    Filter.process_packet(pkt)
    count += 1
    total_bytes += pkt['Size']
