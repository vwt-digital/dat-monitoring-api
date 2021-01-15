import base64
import json
import logging
from functools import reduce

import config

from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()


def get_issue_title(title_type, payload):
    issue_type = config.ISSUE_TITLES[title_type]
    variables = {}
    for key, value in issue_type['variables'].iteritems():
        variables[key] = get_variable_value(payload=payload, keys=value)
    return issue_type['title'].format(**variables)


def check_conditions(title_type, payload):
    issue_type = config.ISSUE_TITLES[title_type]
    for condition in issue_type['conditions']:
        if get_variable_value(payload=payload, keys=condition['variable']) not in condition['shouldBe']:
            return False
    return True


def get_variable_value(payload, keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, payload)


def topic_to_topic(request):
    # Extract data from request
    envelope = json.loads(request.data.decode('utf-8'))
    payload = json.loads(base64.b64decode(envelope['message']['data']))

    # Extract subscription from subscription string
    try:
        subscription = envelope['subscription'].split('/')[-1]
        logging.info(f'Message received from {subscription} {payload}')
    except Exception as e:
        logging.info('Extract of subscription failed')
        logging.exception(e)
        return 'Conflict', 409

    if not check_conditions(title_type=subscription, payload=payload):
        logging.info(f'Not formatting issue from {subscription} because of failing conditions.')
    elif hasattr(config, 'ISSUE_TITLES'):
        title = get_issue_title(title_type=subscription, payload=payload)

        formatted = base64.b64decode({title: payload})

        # Publish to ops-issues here
        topic_path = publisher.topic_path(config.ODH_PROJECT, config.OPS_ISSUES)
        publisher.publish(topic_path, formatted)
    else:
        logging.info(f'Not formatting issue from {subscription} because of development subscription.')

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successful, no further actions needed
    return 'OK', 204
