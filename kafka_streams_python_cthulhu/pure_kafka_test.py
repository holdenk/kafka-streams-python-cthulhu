import time
import logging
from pykafka import KafkaClient
from pykafka.test.utils import get_cluster, stop_cluster
from kafka_streams_python_cthulhu.strlen import transform
from kafka_streams_python_cthulhu.pure_kafka_value_transformer import PureKafkaValueTransformer
import unittest2

class BasicPureKafkaTest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = logging.getLogger(__name__)
        cls._logger.setLevel(logging.DEBUG)
        cls._kafka = get_cluster()
        cls._connection = cls._kafka.connection
        cls._client = KafkaClient(cls._kafka.brokers)
        topics=["in", "out", "fail"]
        map(lambda topic: cls._kafka.create_topic(topic, 3, 2), topics)
        wait_count = 2
        attempts = 0
        cls._client.update_cluster()
        while attempts < wait_count:
            if "in" not in cls._client.topics:
                cls._logger.debug("in not found in topics, waiting")
                time.sleep(1)
                cls._client.update_cluster()
            else:
                break
            attempts = attempts + 1

        if "in" not in cls._client.topics:
            raise Exception(
                "Client topics {0} do not include required input topic"
                .format(cls._client.topics))
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
