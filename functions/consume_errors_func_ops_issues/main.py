import base64
import json
import logging
import config

from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()


def topic_to_topic(request):

    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])

    # Extract subscription from subscription string
    try:
        subscription = envelope['subscription'].split('/')[-1]
        logging.info(f'Message received from {subscription} [{payload}]')

        # Publish to ops-issues here
        topic_path = publisher.topic_path(config.ODH_PROJECT, config.OPS_ISSUES)
        publisher.publish(topic_path, payload)

    except Exception as e:
        logging.info('Extract of subscription failed')
        logging.exception(e)
        return 'Conflict', 409

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successfull, no further actions needed
    return 'OK', 204
