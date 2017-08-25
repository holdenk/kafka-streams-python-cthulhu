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
import logging
import os

if 'IS_TEST' not in os.environ and "JARS" not in os.environ:
    VERSION = '0.0.1'
    JAR_FILE = 'cthulhu_2.11-' + VERSION + '.jar'
    DEV_JAR = 'cthulhu_2.11-' + VERSION + '-SNAPSHOT.jar'
    my_location = os.path.dirname(os.path.realpath(__file__))
    local_prefixes = [
        # For development, use the sbt target scala-2.11 first
        # since the init script is in sparklingpandas move up one dir
        os.path.join(my_location, '../target/scala-2.11/'),
        # Also try the present working directory
        os.path.join(os.getcwd(), '../target/scala-2.11/'),
        os.path.join(os.getcwd(), 'target/scala-2.11/')]
    prod_jars = [os.path.join(prefix, JAR_FILE) for prefix in local_prefixes]
    dev_jars = [os.path.join(prefix, DEV_JAR) for prefix in local_prefixes]
    jars = prod_jars + dev_jars
    try:
        jars.append(os.path.abspath(resource_filename('cthulhu.jar',
                                                      JAR_FILE)))
    except Exception as e:
        print("Could not resolve resource file %s. This is not necessarily"
              " (and is expected during development) but should not occur in "
              "production if pip installed." % str(e))
    jar = ""
    try:
        jar = [jar_path for jar_path in jars if os.path.exists(jar_path)][0]
    except IndexError:
        raise IOError("Failed to find jars. Looked at paths %s." % jars)
    original_classpath = os.environ.get("CLASSPATH", "")
    if original_classpath.find(jar) != -1:
        classpath = "{0}:{1}".format(jar, original_classpath)
    logging.debug("Found jar of {0} and set class path to {1}".format(
        jar, classpath))
    os.environ["JARS"] = jar
    os.environ["CLASSPATH"] = classpath
