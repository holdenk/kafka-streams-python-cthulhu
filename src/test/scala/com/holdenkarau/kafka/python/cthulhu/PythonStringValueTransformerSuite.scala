/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.holdenkarau.kafka.python.cthulhu;

import org.apache.kafka.clients.consumer.ConsumerRecord
import org.apache.kafka.common.serialization.Serdes
import org.apache.kafka.streams.kstream._
import org.apache.kafka.streams.processor.TimestampExtractor
import org.apache.kafka.streams.{KeyValue, StreamsConfig}

import java.lang.ProcessBuilder
import java.io._
import java.util.Properties

import org.scalatest.{FlatSpec, Matchers}

import com.madewithtea.mockedstreams._

class PythonStringValueTransformerSuite extends FlatSpec with Matchers {
  it should "have the same result length as input" in {
    import Fixtures.Basic._

    val output = MockedStreams()
      .topology(topology _)
      .input(InputTopic, strings, strings, input)
      .outputTable(OutputTopic, strings, strings, expected.size)

    output shouldEqual expected.toMap
  }

  object Fixtures {
    object Basic {
      def topology(builder: KStreamBuilder) = {
        val testFuncFile = "kafka_streams_python_cthulhu/strlen.py"
        val stream: KStream[String, String] =
          builder.stream(strings, strings, InputTopic)
            .transformValues(PythonStringValueTransformerSupplier(testFuncFile))
        stream.to(strings, strings, OutputTopic)
      }
      val InputTopic = "input"
      val OutputTopic = "output"
      val strings = Serdes.String()

      val input = Seq(("k1", "v1"), ("k2", "v2p"))
      val expected = Seq(("k1", "2"), ("k2", "3"))
    }
  }
}
