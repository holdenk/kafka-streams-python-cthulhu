#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function

import copy
from multiprocessing import Process, Queue
from pykafka import KafkaClient
import time
import logging

class PureKafkaValueTransformer(object):

    def __init__(self,
                 brokers,
                 consumer_kwargs,
                 producer_kwargs,
                 transform_function,
                 in_topic,
                 out_topic,
                 backoff=0.01,
                 failure_topic=None,
                 num_processes=2):
        def _worker_loop():
            self._logger = logging.getLogger(__name__)
            while True:
                try:
                    _process_stream()
                except Exception as e:
                    self._logger.warn("Uncaught {0} in main loop, reconnecting"
                                .format(repr(e)))
        def _process_msgs(producer, consumer, failure_producer):
            did_work = False
            # Non blocking fetch and process the error message
            message = consumer.consume(block=False)
            if message:
                did_work = True
                try:
                    result = transform_function(message.value)
                    producer.produce(result)
                except Exception as e:
                    error_msg = ("Exception {0} processing message {1}"
                                 .format(repr(e), message))
                    self._logger.warn(error_msg)
                    if failure_producer:
                        try:
                            failure_producer.produce(error_msg)
                        except Exception as e2:
                            self._logger.warn("{0} during error reporting"
                                         .format(repr(e2)))
            # If delivery reports are enabled look for failures
            if producer_kwargs['delivery_reports']:
                try:
                    msg, exc = producer.get_delivery_report(block=False)
                    # Processing a delivery report (success or failure) counts as work.
                    did_work = True
                except Queue.Empty:
                    exc = None
                if exc is not None:
                    error_msg = ("Kafka failure {0} delivering {1}"
                                 .format(repr(exc), msg))
                    self._logger.warn(error_msg)
                    if failure_producer:
                        try:
                            failure_producer.produce(error_msg)
                        except Exception as e2:
                            self._logger.warn("{0} during error reporting"
                                         .format(repr(e2)))
            # If we didn't have a message wait a bit
            if not did_work:
                self._logger.debug("No msg received, waiting {0}".format(backoff))
                time.sleep(backoff)

        def _process_stream():
            client = KafkaClient(brokers)
            # Construct the producer & consumer
            producer = client.topics[out_topic].get_producer(
                **producer_kwargs)
            try:
                consumer = client.topics[in_topic].get_balanced_consumer(
                    **consumer_kwargs)
            except Exception as e:
                msg = ("Error constructing consumer {0} with args {1}"
                       .format(repr(e), consumer_kwargs))
                raise Exception(msg)
            failure_producer = None
            if failure_topic is not None:
                failure_producer_kwargs = copy.deepcopy(producer_kwargs)
                failure_producer_kwargs['delivery_reports'] = False
                failure_producer = client.topics[failure_topic].get_producer(
                    **producer_kwargs)

            while True:
                _process_msgs(producer, consumer, failure_producer)

        client = KafkaClient(brokers)
        # Verify topics exists
        if in_topic not in client.topics:
            raise Exception(
                "Input topic {0} not found in available topics {1}"
                .format(in_topic, client.topics))
        if out_topic not in client.topics:
            raise Exception(
                "Output topic {0} not found in available topics {1}"
                .format(out_topic, client.topics))
        if (failure_topic is not None and
            failure_topic not in client.topics):
            raise Exception(
                "Failure topic {0} not found in available topics {1}"
                .format(failure_topic, client.topics))

        # Set some default values on consumer/producer.
        if 'consumer_group' not in consumer_kwargs:
            logging.debug("consumer_group was not specified in consumer_kwargs"
                         "setting to a hash of the provided transformation")
            consumer_kwargs['consumer_group'] = str(hash(transform_function))

        if 'zookeeper_connect' not in consumer_kwargs:
            logging.warn("zookeeper_connect not specified in consumer_kwargs")
            raise Exception("Need zookeeper_connect in consumer_kwargs")

        if 'delivery_reports' not in producer_kwargs:
            logging.debug(
                "delivery_reports not set in producer_kwargs, enabling")
            producer_kwargs['delivery_reports'] = True

        # Start the sub processes
        self._processes = map(lambda x: Process(target=_worker_loop, args=()),
                              range(num_processes))
        map(lambda p: p.start(), self._processes)

    def stop_all(self):
        map(lambda x: x.terminate(), self._processes)

    def running(self):
        """
        Return the number of processes still running.
        """
        return len(filter(lambda x: x.is_alive(), self._processes))
