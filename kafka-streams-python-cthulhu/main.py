#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
A basic wrapper for transformers. Right now this is pure string->string
which may summon cthulhu, may he eat your soul last, and in the future
should be replaced with an Arrow based solution less likely to disturb
the great old ones.

In case this isn't clear, don't use this in production, yet. Unless you
really really like lovecraft - in which case support contracts are available.
"""
import sys
import socket
import struct


def _read_int(stream):
    length = stream.read(4)
    if not length:
        raise EOFError
    return struct.unpack("!i", length)[0]


def _write_int(value, stream):
    stream.write(struct.pack("!i", value))


def main(socket):
    while (True):
        input_length = _read_int(socket)
        data = socket.read(input_length)
        result = transform(data)
        resultBytes = result.encode()
        _write_int(len(resultBytes), socket)
        socket.write(resultBytes)
        socket.flush()


if __name__ == '__main__':
    # Read a local port to connect to from stdin
    java_port = int(sys.stdin.readline())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", java_port))
    sock_file = sock.makefile("rwb", 65536)
    main(sock_file)
