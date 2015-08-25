# -*- encoding: utf-8 -*-
"""
CollectD plugin which measures NTP offsets
"""
# TODO - discount wildly different responses

from __future__ import division
import datetime

import collectd
from dns.exception import DNSException
import dns.resolver
import ntplib


INTERVAL = 60


def warn(msg):
    collectd.warning('collectd_ntp plugin: {msg}'.format(msg=msg))


class NtpOffsetConfigException(Exception):
    pass


class NtpOffset(object):
    PLUGIN_NAME = 'ntpoffset'

    def __init__(self, config=None):
        self.pool = None
        self.ntp_client = ntplib.NTPClient()
        if config:
            self.config(config)

    def config(self, conf):
        entries = [node for node in conf.children if node.key == 'pool']

        try:
            self.pool = entries[0].values[0]

        except IndexError:
            raise NtpOffsetConfigException('No pool specified')

    def read(self):
        offsets = self.offsets()
        if offsets:
            self.submit_average(offsets)
            self.submit_min(offsets)
            self.submit_max(offsets)

    def offsets(self):
        return filter(
            lambda offset: offset is not None,
            [self.server_offset(server) for server in self.pool_servers()])

    def server_offset(self, server):
        try:
            return self.ntp_client.request(server).offset

        except ntplib.NTPException:
            warn('failed to read offset from {server}'.format(server=server))
            return None

    def pool_servers(self):
        return [rdata.address for rdata in self.query_pool_dns()]

    def query_pool_dns(self):
        try:
            return dns.resolver.query(self.pool, 'A').response.answer[0].items

        except (DNSException, AttributeError, IndexError):
            warn('query pool dns failed: {pool}'.format(pool=self.pool))
            return []

    def submit_average(self, offsets):
        print offsets
        self.submit('average', [sum(offsets) / float(len(offsets))])

    def submit_min(self, offsets):
        self.submit('min', [float(min(offsets))])

    def submit_max(self, offsets):
        self.submit('max', [float(max(offsets))])

    def submit(self, type_instance, values):
        v = collectd.Values()
        v.plugin = self.PLUGIN_NAME
        v.plugin_instance = 'offset'
        v.type = 'time_offset'
        v.type_instance = type_instance
        v.time = datetime.datetime.now().isoformat()
        v.values = values
        v.dispatch()


ntpoffset = NtpOffset()
collectd.register_config(ntpoffset.config)
collectd.register_read(ntpoffset.read, INTERVAL)
