#!/usr/bin/env python

import os
import ConfigParser
from pymongo import MongoClient

CONFIG_FILE = '/etc/otfnfv.cfg'

if not os.path.isfile(CONFIG_FILE):
    print "Make sure you have a %s file in /etc !" % 'otfnfv.cfg'
    exit(1)

def connect():
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)

    host = config.get('mongodb', 'host')
    port = config.getint('mongodb', 'port')
    db_name = config.get('mongodb', 'db')

    conn = MongoClient(host, port)

    return conn[db_name]


available_filters = [
    {'_id': 'Source IP'},
    {'_id': 'Destination IP'},
    {'_id': 'Source Port'},
    {'_id': 'Destination Port'},
    {
        '_id': 'Protocol',
        'options': [
            'Any',
            'ICMP',
            'ICMPv6',
            'Ethernet',
            'ARP',
            'IPv6',
            'IP',
            'UDP',
            'TCP',
            'BOOTP',
            'DNS'
        ]
    }
]

conn = connect()

filter_collection = conn['filters']
doc_collection = conn['control']
vnf = conn['vnf']

filter_collection.drop()
doc_collection.drop()
vnf.drop()

for f in available_filters:
    filter_collection.insert_one(f)

doc_control = {
    'vnf': {
        'to_instantiate': '',
        'to_kill': '',
        'create_connection': '',
        'working': False,
    },
    'rule': {
        'dirty': False
    },
    'network': {
        'stop': False,
        'switch': []
    }
}


doc_collection.insert(doc_control)

vnf.insert(
    {
        '_id': 'filter',
        'script': 'filter.py'
    }
)

vnf.insert(
    {
        '_id': 'Statistics',
        'script': 'statistics.py',
        'port': 5001
    }
)

vnf.insert(
    {
        '_id': 'DPI',
        'script': 'dpi.py',
        'port': 5002
    }
)

vnf.insert(
    {
        '_id': 'Anomaly Detection',
        'script': 'traffic_anomaly.py',
        'port': 5003
    }
)
