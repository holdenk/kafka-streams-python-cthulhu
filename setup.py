from setuptools import setup, find_packages

VERSION = '0.0.1'
JAR_FILE = 'cthulhu-' + VERSION + '.jar'

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
    install_requires=[
        'future',
        'pykafka',
        'multiprocessing',
    ],
    tests_requires=[
        'nose==1.3.7',
        'coverage>3.7.0',
        'unittest2>=1.0.0',
        'testinstances',
    ],
)
