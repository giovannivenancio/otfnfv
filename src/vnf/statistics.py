#!/usr/bin/env python

import time
import os
import sys
import socket
import ast
import threading
from utils import *

socket_file = '/var/run/statistics_socket'

# Make sure the socket does not already exist
try:
    os.unlink(socket_file)
except OSError:
    if os.path.exists(socket_file):
        raise

class Statistics():

    def __init__(self):
        self.conn, self.db = connect('remote')
        self.results = self.conn['results']['results_stats']

        # Collections
        self.coll_rules = self.db['rules']
        self.coll_vnf = self.db['vnf']

        self.socket_file = socket_file
        port = self.coll_vnf.find_one({'_id': 'Statistics'}, {'port': 1})['port']

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.socket_file)

        self.socket.listen(1)

    def create_results(self, rule):
        """
        Create rule results
        """

        doc = {'_id': rule}

        doc['Total Packets'] = 0
        doc['Total Bytes'] = 0

        self.results.insert(doc)

        return doc

    def update_document(self, rule_id, pkt):
        """
        Update a document
        """

        results[rule_id]['Total Packets'] += 1
        results[rule_id]['Total Bytes'] += pkt['Size']

    def update_data(self):
        """
        Write to database in-memory results
        """

        conn, db = connect('remote')
        coll_results = conn['results']['results_stats']

        while True:
            time.sleep(1)

            for rule_id, node_result in results.iteritems():
                coll_results.update_one(
                    {'_id': rule_id},
                    {
                        '$set': {
                            'Total Packets': node_result['Total Packets'],
                            'Total Bytes': node_result['Total Bytes']
                        }
                    })

global results
results = {}

statistic = Statistics()
connection = statistic.socket.accept()[0]

updater = threading.Thread(target=statistic.update_data)
updater.start()

while True:
    size = connection.recv(3)
    data = connection.recv(int(size))

    data = data.replace("'", "\"")
    pkt = ast.literal_eval(data)

    for rule_id in pkt['rules']:
        if not statistic.results.count({'_id': rule_id}):
            results[rule_id] = statistic.create_results(rule_id)

        statistic.update_document(rule_id, pkt)
