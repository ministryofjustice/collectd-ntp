collectd_ntp
============

.. image:: https://travis-ci.org/ministryofjustice/collectd-ntp.svg?branch=master
    :target: https://travis-ci.org/ministryofjustice/collectd-ntp

A collectd plugin to fetch NTP offsets from a pool.

The default update interval is 60 seconds.

Installation
------------

The latest stable version can be installed from PyPI_:

.. code:: shell

    $ pip install collectd-ntp

.. _PyPI: https://pypi.python.org/pypi


Configuration
~~~~~~~~~~~~~

To configure the plugin:

.. code:: xml

    <LoadPlugin python>
      Globals true
    </LoadPlugin>

    <Plugin python>
      Import "ntpoffset"

      <Module "ntpoffset">
        # NTP pool address
        pool "pool.ntp.org"
      </Module>
    </Plugin>
