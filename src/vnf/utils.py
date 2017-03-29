#!/usr/bin/env python

import ConfigParser
import subprocess
from pymongo import MongoClient

# Settings file
CONFIG_FILE = '/etc/otfnfv.conf'

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

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

