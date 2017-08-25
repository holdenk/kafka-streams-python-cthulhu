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

import time
import logging
from pykafka import KafkaClient
from pykafka.test.utils import get_cluster, stop_cluster
from .strlen import transform
from .pure_kafka_value_transformer import PureKafkaValueTransformer
import unittest2


class BasicPureKafkaTest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = logging.getLogger(__name__)
        cls._logger.setLevel(logging.DEBUG)
        cls._kafka = get_cluster()
        topics = ["in", "out", "fail"]
        list(map(lambda topic: cls._kafka.create_topic(topic, 3, 2), topics))
        cls._connection = cls._kafka.connection
        cls._client = KafkaClient(cls._kafka.brokers)
        if "in" not in cls._client.topics:
            cls._logger.debug("in not found in topics, waiting")
            time.sleep(1)
            cls._client.update_cluster()

        if "in" not in cls._client.topics:
            msg = ("Client topics {0} do not include required input topic"
                   .format(cls._client.topics))
            cls._logger.error(msg)
            raise Exception(msg)

        cls._transformer = PureKafkaValueTransformer(
            brokers=cls._kafka.brokers,
            consumer_kwargs={'zookeeper_connect': cls._kafka.zookeeper},
            producer_kwargs={},
            transform_function=transform,
            in_topic="in",
            out_topic="out",
            backoff=1.0,
            failure_topic="fail")

    @classmethod
    def tearDownClass(cls):
        cls._transformer.stop_all()
        stop_cluster(cls._kafka)

    def test_simple_strlen(self):
        print("Hi! writing data out")
        producer = self._client.topics["in"].get_producer(sync=True)
        result_consumer = self._client.topics["out"].get_simple_consumer(
            consumer_group="test")
        producer.produce("hi boo")
        print("Written out")
        print("fetching message")
        for message in result_consumer:
            if message is not None:
                print("Fetched message {0} {1}".format(message, message.value))
                self.assertEqual(message.value, "6")
                break
        self.assertEqual(self._transformer.running(), 2)

if __name__ == '__main__':
    unittest2.main()
