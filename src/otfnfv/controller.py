#!/usr/bin/env python

import os
import time
import threading
from subprocess import call
from utils      import *

class Controller():

    def __init__(self):
        # Connection
        self.conn, self.db = connect(None)

        self.conn.drop_database('results')
        self.results = self.conn['results']

        # Collections
        self.coll_rules   = self.db['rules']
        self.coll_filters = self.db['filters']
        self.coll_vnf     = self.db['vnf']
        self.control      = self.db['control']
        self.statistics   = self.results['results_stats']

        self.active_vnfs = []

        self.clear_rules()

        graph_thread = threading.Thread(target=self.graph_data)
        graph_thread.start()

    def close(self):
        """
        Close MongoDB connection
        """

        self.conn.close()

    def graph_data(self):
        """
        Get graph data every 30 seconds
        """

        global graph_results
        global rule_ids

        # Create database connection on thread
        conn, db = connect(None)
        results = conn['results']
        statistics = results['results_stats']

        rule_ids = []
        graph_results = {}

        total = 0
        count = 0

        while True:
            for rule_id in rule_ids:
                result = statistics.find_one({'_id': rule_id})

                if result:
                    count = result['Total Packets'] - count
                    total = result['Total Bytes'] - total

                    graph_results[rule_id]['Total Packets'].append(count)
                    graph_results[rule_id]['Total Bytes'].append(total)

                    count = result['Total Packets']
                    total = result['Total Bytes']

            time.sleep(1)

    def get_graph_results(self):
        """
        Return results of graph thread
        """

        return graph_results

    def insert_rule(self, rule):
        """
        Insert a new rule on MongoDB
        """

        # Store rule on database
        self.coll_rules.insert_one(rule)

        rule_ids.append(rule['_id'])
        graph_results[rule['_id']] = {'Total Packets': [], 'Total Bytes': []}

        # Check if vnf isn't already instantiated
        if rule['vnf'] not in self.active_vnfs:
            self.instance_vnf(rule['vnf'])
            self.active_vnfs.append(rule['vnf'])
        else:
            # Just update rules on filter
            self.control.find_one_and_update({}, {
                '$set': { 'rule.dirty': True }
            })

    def delete_rule(self, rule):
        """
        Remove a rule from MongoDB
        """

        # First stop the rule, then remove it
        self.stop_rule(rule)
        self.coll_rules.delete_one({'_id': rule['_id']})

    def stop_rule(self, rule):
        """
        Stop a rule in VNF-filter
        """

        rules_count = self.coll_rules.count({
            'vnf': rule['vnf']
        })

        # If it is the last rule with that VNF, kill it
        if rules_count == 1:
            self.control.find_one_and_update({}, {
                '$set': {
                    'vnf.to_kill': rule['vnf'],
                    'vnf.working': True
                },
            })

            self.active_vnfs.remove(rule['vnf'])

        # Wait for network kill vnf
        while self.control.find_one({}, {'vnf': 1})['vnf']['working']:
            pass
        else:
            # Set dirty flag to vnf-filter
            self.control.find_one_and_update({}, {
                '$set' : { 'rule.dirty': True }
            })

    def instance_vnf(self, vnf):
        """
        Instance a new VNF
        """

        # Put VNF on queue and tag as working
        self.control.find_one_and_update({}, {
            '$set': {
                'vnf.to_instantiate': vnf,
                'vnf.working': True
            },
        })

        # Wait network finish VNF instantiation
        while self.control.find_one({}, {'vnf': 1})['vnf']['working']:
            pass
        else:
            # Set dirty flag to vnf-filter
            self.control.find_one_and_update({}, {
                '$set' : { 'rule.dirty': True }
            })

    def get_rules(self):
        """
        Get all rules
        """

        return [rule for rule in self.coll_rules.find()]

    def get_results(self, rule_id):
        """
        Return results of VNF's
        """

        results = self.statistics.find_one({'_id': rule_id})

        return [results['Total Packets'], results['Total Bytes']]

    def get_switches(self):
        """
        Get all switches pids
        """

        return self.control.find_one({}, {'network': 1})['network']['switch']

    def clear_rules(self):
        """
        Remove all rules from MongoDB
        """

        self.coll_rules.delete_many({})

    def list_filters(self):
        """
        List available filters
        """

        return [str(filters['_id']) for filters in self.coll_filters.find()]

    def list_protocols(self):
        """
        List available protocols
        """

        return self.coll_filters.find_one(
            {'_id': 'Protocol'},
            {'options': 1})['options']

    def list_vnf(self):
        """
        List available VNF's
        """

        vnfs = self.coll_vnf.find({'_id': {'$ne': 'filter'}})

        return [str(vnf['_id']) for vnf in vnfs]

    def list_rules(self):
        """
        List created rules
        """

        return [vnf for vnf in self.coll_rules.find()]

    def start_network(self):
        """
        Start network
        """

        mininet = PATH + 'otfnfv/network.py'

        cmd = [mininet, '&']

        execute(cmd)

    def stop_network(self):
        """
        Stop network
        """

        self.control.find_one_and_update({}, {
            '$set' : { 'network.stop': True }
        })

        exit_network(None, None)

        self.conn.close()
