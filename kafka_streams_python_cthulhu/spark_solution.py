from pyspark import *
from pyspark.sql import *
from pyspark.streaming.kafka import *

def do_dstreams():
     # DStreams

     kafkaStream = KafkaUtils.createDirectStream(
          ssc, "ex", {"bootstrap.servers": bootstrap_servers})
     processed = kafkaStream.map(transform)

     def write_to_kafka(partition):
          producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
          for x in partition:
               producer.send("output", x)

          processed.foreachRDD(lambda rdd: rdd.foreachPartition(write_to_kafka))
          # But (for now) this summons Cthulhu anyways :(


def do_structured():
     # Structured Streaming

     spark = SparkSession.builder.getOrCreate()


     df = spark.readStream.format("kafka") \
                          .option("kafka.bootstrap.servers", servers) \
                          .option("subscribe", "in")  \
                          .load()
     kv_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
     udf = UserDefinedFunction(transform_function, IntegerType(), "pstrlen")
     result = kv_df.select("key", udf("value").alias("value"))
     result.writeStream \
           .format("kafka") \
           .option("kafka.bootstrap.servers", servers) \
           .option("topic", "output")


