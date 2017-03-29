#!/usr/bin/env python

import os.path
import ConfigParser
import subprocess
from pymongo import MongoClient

# Settings file
CONFIG_FILE = '/etc/otfnfv.conf'

if not os.path.isfile(CONFIG_FILE):
    print "Make sure you have a %s file in /etc !" % 'otfnfv.conf'
    exit(1)

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

# Source path
PATH = config.get('system', 'path')

# Network interface
INTERFACE = config.get('system', 'interface')

# Ryu config
RYU_PATH = config.get('ryu', 'path')
RYU_APP = config.get('ryu', 'app')
RYU_PORT = config.getint('ryu', 'port')
RYU_APP_PATH = RYU_PATH + RYU_APP

def connect(conn_request):
    """
    Connect with MongoDB
    """

    if conn_request == 'remote':
        host = config.get('mongodb', 'remote_host')
    else:
        host = config.get('mongodb', 'host')

    port = config.getint('mongodb', 'port')
    db_name = config.get('mongodb', 'db')

    conn = MongoClient(host, port)
    db = conn[db_name]

    return [conn, db]

def execute(cmd):
    """
    Execute a command in another process
    """

    subprocess.Popen(cmd)

def exit_network(signal, frame):
    """
    On program exit or crash, do the necessary cleanup
    """

    commands = [
        (['pkill', '-f', 'network.py'], 'Network'),
        (['pkill', '-f', 'ryu-manager'], 'Ryu'),
        (['pkill', '-f', 'controller.py'], 'Interface Controller'),
        (['pkill', '-f', 'filter.py'], 'Filter Manager'),
        (['mn', '-c', '-v', 'output'], 'Cleaning network'),
    ]

    for cmd in commands:
        print "Killing %s" % cmd[1]
        subprocess.call(cmd[0])

    mg, db = connect(None)
    control = db['control']
    rules = db['rules']

    print "Reset control document"
    control.delete_one({})

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

    control.insert_one(doc_control)

    # Remove all created rules
    rules.delete_many({})

    print "Killing main process"
    subprocess.call(['pkill', '-f', 'otfnfv'])
