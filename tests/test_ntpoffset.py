# -*- encoding: utf-8 -*-
"""NTP offset collectd plugin tests"""

from __future__ import division, with_statement
import collections
import contextlib
import datetime
import mock
import unittest

from dns.exception import DNSException
import ntplib


class MockConfig(mock.Mock):

    def __init__(self, **kwargs):
        super(MockConfig, self).__init__()
        self.children = [
            mock.Mock(key=key, values=values)
            for key, values in kwargs.iteritems()]


test_pool = [
    '0.0.0.0',
    '1.1.1.1']


Metrics = collections.namedtuple('Metrics', ('avg', 'min', 'max'))
ExpectedMetric = collections.namedtuple('ExpectedMetric', (
    'type_instance', 'values'))


def mock_metrics():
    return Metrics(mock.Mock(), mock.Mock(), mock.Mock())


@contextlib.contextmanager
def dns_query(answer=[]):
    with mock.patch('ntpoffset.dns') as dns:
        query = dns.resolver.query
        reply = query.return_value
        reply.response.answer = [
            mock.Mock(items=[
                mock.Mock(address=address) for address in answer])]
        yield query


@contextlib.contextmanager
def ntp_offsets(offsets):
    with mock.patch('ntplib.NTPClient') as NTPClient:
        ntp_client = NTPClient.return_value
        ntp_client.request.side_effect = [
            mock.Mock(offset=offset) for offset in offsets]
        yield ntp_client.request


def raise_exception(exc):

    def fn(*args, **kwargs):
        raise exc

    return fn


class NtpOffsetPluginTest(unittest.TestCase):

    def setUp(self):
        self.collectd = mock.Mock()
        self.modules_patch = mock.patch.dict(
            'sys.modules', {'collectd': self.collectd})
        self.modules_patch.start()
        import ntpoffset
        self.ntpoffset = ntpoffset

    def tearDown(self):
        self.modules_patch.stop()

    def plugin(self, *args):
        return self.ntpoffset.NtpOffset(*args)

    def test_plugin_identifies_itself(self):
        self.assertEqual('ntpoffset', self.plugin().PLUGIN_NAME)

    def test_minimal_config_requires_pool_name(self):
        try:
            self.plugin(MockConfig(foo=[]))
        except self.ntpoffset.NtpOffsetConfigException:
            pass
        else:
            self.fail('NtpOffsetConfigException not raised')

    def test_minimal_config_is_valid(self):
        try:
            self.plugin(MockConfig(pool=['127.0.0.1']))
        except Exception as e:
            self.fail(e)

    def test_plugin_queries_each_server_in_pool(self):
        addr = '127.0.0.1'
        config = MockConfig(pool=[addr])
        offsets = range(len(test_pool))

        with dns_query(test_pool) as dns_resolver:
            with ntp_offsets(offsets) as ntp_request:

                self.plugin(config).read()

                dns_resolver.assert_called_with(addr, 'A')

                ntp_request.assert_has_calls([
                    mock.call(address)
                    for address in test_pool])

    def test_metric_is_avg_min_and_max_offset(self):
        config = MockConfig(pool=['127.0.0.1'])
        offsets = [-0.13579, 0.2468]
        expected = [
            ExpectedMetric('average', [sum(offsets) / len(offsets)]),
            ExpectedMetric('min', [min(offsets)]),
            ExpectedMetric('max', [max(offsets)])
        ]

        with ntp_offsets(offsets):
            with dns_query(test_pool):

                metrics = mock_metrics()
                self.collectd.Values.side_effect = metrics

                self.plugin(config).read()

                for metric, expected in zip(metrics, expected):
                    assert metric.dispatch.called
                    self.assertEqual(
                        expected.type_instance, metric.type_instance)
                    self.assertEqual(expected.values, metric.values)

    def test_nothing_submitted_if_no_pool_servers(self):
        config = MockConfig(pool=['127.0.0.1'])

        with dns_query([]) as dns_resolver:

            dns_resolver.side_effect = raise_exception(
                DNSException('Some DNS problem'))

            self.plugin(config).read()

            self.collectd.Values.assert_has_calls([])

    def test_nothing_submitted_if_no_servers_respond(self):
        config = MockConfig(pool=['127.0.0.1'])

        with dns_query(test_pool):
            with ntp_offsets([None, None]) as ntp_request:

                ntp_request.side_effect = raise_exception(
                    ntplib.NTPException('No response received from host.'))

                self.plugin(config).read()

                self.collectd.Values.assert_has_calls([])

    def test_metric_submitted_if_at_least_one_server_responds(self):
        config = MockConfig(pool=['127.0.0.1'])

        with dns_query(test_pool):
            with ntp_offsets([None, 0.13579]):

                metrics = mock_metrics()
                self.collectd.Values.side_effect = metrics

                self.plugin(config).read()

                for metric in metrics:
                    self.assertEqual([0.13579], metric.values)

    def test_metric_has_unix_timestamp(self):
        config = MockConfig(pool=['127.0.0.1'])

        with dns_query(test_pool):
            with ntp_offsets([0.1234, 0.2345]):

                metrics = mock_metrics()
                self.collectd.Values.side_effect = metrics

                self.plugin(config).read()

                now = datetime.datetime.now()
                tolerance = datetime.timedelta(seconds=3)
                for metric in metrics:
                    time = datetime.datetime.utcfromtimestamp(metric.time)
                    self.assertTrue(tolerance > now - time)
