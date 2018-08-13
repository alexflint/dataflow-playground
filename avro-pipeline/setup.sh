gcloud pubsub topics create avro-data-staging-events
gsutil mb gs://avro-data-staging
gsutil notification create -t avro-data-staging-events -f json gs://avro-data-staging

# not necessary because dataflow creates a subscription per pipeline
#gcloud pubsub subscriptions create --topic avro-data-staging-events avro-data-staging-subscription
