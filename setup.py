from setuptools import setup, find_packages
import sys

VERSION = '0.0.1'
JAR_FILE = 'cthulhu-' + VERSION + '.jar'

if sys.version_info[0] < 3:
    INSTALL_REQS = [
        'future',
        'pykafka',
        'multiprocessing',
        'gevent',
    ]
else:
    INSTALL_REQS = [
        'future',
        'pykafka',
        'gevent',
    ]

setup(
    name='kafka_streams_python_cthulhu',
    version=VERSION,
    author='Holden Karau',
    author_email='holden@pigscanfly.ca',
    # Copy the shell script into somewhere likely to be in the users path
    packages=find_packages(),
    url='https://github.com/holdenk/kafka-streams-python-cthulhu',
    include_package_data = True,
    package_data = {
        'cthulhu.jar' : ["jar/" + JAR_FILE]},
    license='LICENSE',
    description='Proof of concept adventures with Python and Kafka',
    long_description=open('README.md').read(),
    test_suite='nose.collector',
    install_requires=INSTALL_REQS,
    tests_requires=[
        'nose==1.3.7',
        'coverage>4.0.0',
        'unittest2>=1.0.0',
        'testinstances',
    ],
)
