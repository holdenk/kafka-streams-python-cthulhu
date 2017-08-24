from pykafka import KafkaClient
from pykafka.test.utils import get_cluster, stop_cluster
from kafka_streams_python_cthulhu.strlen import transform
from kafka_streams_python_cthulhu.pure_kafka_value_transformer import PureKafkaValueTransformer
import unittest2

class BasicPureKafkaTest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._kafka = get_cluster()
        cls._connection = cls._kafka.connection
        cls._client = KafkaClient(cls._kafka.brokers)
        topics=["in", "out", "fail"]
        map(lambda topic: cls._kafka.create_topic(topic, 3, 2), topics)
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

        
if __name__ == '__main__':
  unittest2.main()
