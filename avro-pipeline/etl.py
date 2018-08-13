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
import StringIO

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

from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

import google.cloud.storage


class BlobFetcher(beam.DoFn):
    def __init__(self):
        super(BlobFetcher, self).__init__()

    def process(self, elem):
        # TODO: figure out how to cache the client locally
        gcs = google.cloud.storage.Client()

        event = json.loads(elem)

        bucket = event["bucket"]
        name = event["name"]
        blob = gcs.get_bucket(bucket).blob(name)

        contents = blob.download_as_string()
        print("fetched {}/{}: {} bytes".format(bucket, name, len(contents)))

        rd = DataFileReader(StringIO.StringIO(contents), DatumReader())
        for record in rd:
            print(record)
        return []


def run(argv=None):
    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic',
                        required=True,
                        help='Subscription to read GCS change notifications from.')
    parser.add_argument('--output',
                        required=True,
                        help='Output file to write results to.')
    args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    p = beam.Pipeline(options=pipeline_options)

    # consume pubsub events
    print("Reading from pubsub topic: %s" % args.topic)
    lines = p | 'read_from_pubsub' >> ReadStringsFromPubSub(
        topic=args.topic)

    # fetch the blob for each event
    blobs = (lines | 'fetch_blob' >> beam.ParDo(BlobFetcher()))

    # run the pipeline
    result = p.run()
    print("pipeline started, waiting for completion...")
    result.wait_until_finish()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
