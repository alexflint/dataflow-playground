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

"""A word-counting workflow."""

from __future__ import absolute_import

import argparse
import logging
import re
import json
import uuid

from past.builtins import unicode

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.metrics import Metrics
from apache_beam.metrics.metric import MetricsFilter
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition
from apache_beam.io.gcp.pubsub import ReadStringsFromPubSub


def run(argv=None):
    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        dest='input',
                        default='gs://dataflow-samples/shakespeare/kinglear.txt',
                        help='Input file to process.')
    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to.')
    known_args, pipeline_args = parser.parse_known_args(argv)

    topic = None
    if known_args.input.startswith('pubsub://'):
        # if a topic was specified as input then consume from pubsub
        topic = known_args.input[len('pubsub://'):]
        print("Reading from pubsub topic: %s" % topic)
        print(pipeline_args)
        pipeline_args.append('--streaming')

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    p = beam.Pipeline(options=pipeline_options)

    if topic:
        # if a topic was specified as input then consume from pubsub
        print("Reading from pubsub topic: %s" % topic)
        lines = p | 'read_from_pubsub' >> ReadStringsFromPubSub(topic=topic)
    else:
        # otherwise read the text file[pattern] into a PCollection.
        print("Reading from file: %s" % known_args.input)
        lines = p | 'read_from_file' >> ReadFromText(known_args.input)

    # Count the occurrences of each word.
    def extract_tracks(result):
        r = json.loads(result)
        print("processing a results payload with %d tracks..." %
              len(r['Tracks']))
        for track in r['Tracks']:
            yield track

    tracks = (lines | 'split' >> beam.FlatMap(extract_tracks))

    # Format the counts into a PCollection of strings.
    output = tracks | 'format' >> beam.Map(json.dumps)

    # Write the output using a "Write" transform that has side effects.
    # pylint: disable=expression-not-assigned
    output | 'write_to_file' >> WriteToText(known_args.output)

    # Write the tracks to a bigquery table
    tracks | 'write_to_table' >> WriteToBigQuery(
        'alex-bigquery:simresults.tracks',
        write_disposition=BigQueryDisposition.WRITE_APPEND)

    result = p.run()

    print("waiting for pipeline to complete...")
    result.wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
