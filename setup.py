import os
from setuptools import setup


def pkg_dir(path):
    return os.path.join(os.path.dirname(__file__), path)


with open(pkg_dir('VERSION'), 'r') as f:
    version = f.read().strip()


with open(pkg_dir('README.rst'), 'r') as f:
    readme = f.read()


setup(
    name='collectd-ntp',
    version=version,
    py_modules=['ntpoffset'],
    install_requires=['ntplib>=0.3.3,<1', 'dnspython>=1.12.0,<2'],
    author='Andy Driver',
    author_email='andy.driver@digital.justice.gov.uk',
    maintainer='MOJDS',
    url='https://github.com/ministryofjustice/collectd-ntp',
    description='NTP offsets plugin for collectd',
    long_description=readme,
    license='LICENSE',
    keywords=['python', 'ministryofjustice', 'collectd', 'ntp'],
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Networking :: Time Synchronization']
)
