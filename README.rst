collectd_ntp
============

A collectd plugin to fetch NTP offsets from a pool.

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
      Import "collectd_ntp"

      <Module "collectd_ntp">
        # NTP pool address
        pool "127.0.0.1"
      </Module>
    </Plugin>
