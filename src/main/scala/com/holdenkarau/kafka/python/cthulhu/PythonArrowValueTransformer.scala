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

import org.apache.kafka.streams.KeyValue
import org.apache.kafka.streams.processor._
import org.apache.kafka.streams.kstream._

import java.lang.ProcessBuilder
import java.io._
import java.net._
import java.nio.charset.StandardCharsets
import java.util.Arrays

import scala.collection.mutable
import scala.collection.JavaConverters._

/**
 * A basic class to allow you to more easily implement a transformer in Python.
 * This is a WIP POC and should not be used in production environments.
 */
trait PythonArrowValueTransformer[
  ArrowVectorInputType, ArrowVectorReturnType, InputType, OutputType]
  (val pythonCode: String)
    extends ValueTransformer[InputType, OutputType] {
  val invec: ArrowVectorInputType
  val retvec: ArrowVectorReturnType
  val inSchema: VectorSchemaRoot
  val outSchema: VectorSchemaRoot
  val allocator = new RootAllocator(Integer.MAX_VALUE)
  private var pythonProcess: Process = _
  private var temp: File = _
  var serverSocket: ServerSocket = _
  var workerSocket: Socket = _
  var dataOut: DataOutputStream = _
  var dataIn: DataInputStream = _

  override def init(context: ProcessorContext): Unit = {
    serverSocket =
      new ServerSocket(0, 1, InetAddress.getByAddress(Array(127, 0, 0, 1)))
    val builder =
      try {
        temp = File.createTempFile("pyTransformer", ".py");
        val bw = new BufferedWriter(new FileWriter(temp));
        bw.write(pythonCode);
        bw.close();
        val pythonCodePath = temp.getAbsolutePath();
        new ProcessBuilder("python", pythonCodePath);
      } catch {
        case e: Exception =>
          // If we can't write to a temporary file use -c to execute
          // the code as a command.
          new ProcessBuilder("python", "-c", pythonCode);
      }
    val workerEnv = builder.environment()
    workerEnv.put("PYTHONUNBUFFERED", "YES")
    pythonProcess = builder.start();
    // Tell the worker our port
    val out =
      new OutputStreamWriter(pythonProcess.getOutputStream, StandardCharsets.UTF_8)
    out.write(serverSocket.getLocalPort + "\n")
    out.flush()
    // Wait for it to connect to our socket
    serverSocket.setSoTimeout(1000)
    try {
      workerSocket = serverSocket.accept()
      val outStream = new BufferedOutputStream(workerSocket.getOutputStream)
      dataOut = new DataOutputStream(outStream)
      val inStream = new BufferedInputStream(workerSocket.getInputStream)
      dataIn = new DataInputStream(inStream)
    } catch {
      case e: Exception =>
        throw new Exception("Python process did not connect back :(")
    }
  }

  /**
   * Transformers an individual string value using an already started Python process.
   */
  override def transform(value: InputType): ReturnType = {
    // Encode the data to avoid summoning the great old ones
    invec.clear()
    // Hack assumes single concrete record type
    if (invec.getValueCount() == 0) {
      invec.setInitialCapacity(1)
      invec.allocateNew()
    }
    invec.getMutator.setSafe(0, value)
    val buffer = invec.getBuffers(false).flatten

    // Sockets may still summon the great old ones, in the future shared memory
    // may summon a different kind of evil.
    dataOut.writeInt(buffer.size)
    dataOut.write(buffer.getBytes)
    dataOut.flush()
    val resultSize = dataIn.readInt()
    val result = new Array[Byte](resultSize)
    dataIn.readFully(result)
    // Assume UTF8, what could go wrong? :p
    new String(result)
  }

  @Deprecated
  override def punctuate(timestamp: Long): String = {
    null
  }

  /**
   * Close this processor and clean up the Python process.
   */
  override def close(): Unit = {
    try {
      pythonProcess.destroy();
    } catch {
      case e: Exception =>
        System.err.println("Failed to shutdown python process" + e.getMessage())
    }
    try {
      temp.delete();
    } catch {
      case e: Exception =>
        System.err.println("Failed cleanup python transformer code" + e.getMessage())
    }
    allocator.close()
  }
}
