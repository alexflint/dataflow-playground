#!/bin/bash

INPUT=pubsub://projects/alex-bigquery/topics/sim-results
#INPUT=gs://mock-sim-results/1.json

GOOGLE_APPLICATION_CREDENTIALS=$HOME/.gcloud-credentials/alex-bigquery-293ab2402681.json \
python pipeline.py \
--input $INPUT \
--output gs://mock-sim-pipeline/tracks.json \
--runner DataflowRunner \
--project alex-bigquery \
--temp_location gs://mock-sim-pipeline/tmp
