#!/bin/bash

TOPIC=projects/alex-bigquery/topics/avro-data-staging-events


GOOGLE_APPLICATION_CREDENTIALS=$HOME/.gcloud-credentials/alex-bigquery-293ab2402681.json \
python etl.py \
--topic $TOPIC \
--output out/foo \
--streaming \
--runner DirectRunner \
--temp_location out/tmp
