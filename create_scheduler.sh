gcloud scheduler jobs create pubsub weather-scheduler \
    --schedule="0 */5 * * *" \
    --topic=weather-data \
    --message-body="Trigger weather fetch" \
    --time-zone="Europe/London" \
    --location=europe-west2

