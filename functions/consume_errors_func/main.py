import logging
import json
import base64
import os

from dbprocessor import DBProcessor
from google.api_core import exceptions as gcp_exceptions

parser = DBProcessor()
verification_token = os.environ['PUBSUB_VERIFICATION_TOKEN']


def topic_to_datastore(request):
    if request.args.get('token', '') != verification_token:
        return 'Invalid request', 400

    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))
    payload = base64.b64decode(envelope['message']['data'])

    # Extract subscription from subscription string
    try:
        subscription = envelope['subscription'].split('/')[-1]
        logging.info(f'Message received from {subscription} [{payload}]')

        parser.process(json.loads(payload))
    except gcp_exceptions as e:
        logging.info(f"Extraction failed due to: {e}")
        return 408
    except Exception as e:
        logging.info('Extract of subscription failed')
        logging.debug(e)
        raise e

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successfull, no further actions needed
    return 'OK', 204
