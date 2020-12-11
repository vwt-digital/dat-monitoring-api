import base64
import json
import logging


def topic_to_topic(request):

    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])

    logging.info(payload)
