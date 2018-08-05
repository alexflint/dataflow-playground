#!/bin/bash

INPUT=pubsub://projects/alex-bigquery/topics/sim-results
#INPUT=results/1.json

GOOGLE_APPLICATION_CREDENTIALS=$HOME/.gcloud-credentials/alex-bigquery-293ab2402681.json \
python pipeline.py \
--input $INPUT \
--output out/1.json \
--runner DirectRunner \
--temp_location out/tmp
