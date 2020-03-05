import datetime
import json
import logging
from operator import itemgetter

import config
import requests
from google.api_core import exceptions
from google.cloud import datastore


class Notification(object):
    def __init__(self):
        pass

    def process(self, message):
        logging.info("Processing message {}".format(json.dumps(message)))


class Datastore(object):
    def __init__(self):
        self.ds_client = datastore.Client()

    def retrieve_data(self, properties, interval=60):
        if not validate_dict_keys(("kind", "filters"), properties):
            return None
        elif len(properties['filters']) <= 0:
            logging.error('No filters found for this notification')
            return None

        time_delta = (datetime.datetime.utcnow() - datetime.timedelta(
            minutes=interval)).strftime('%Y-%m-%dT%H:00:00.000000000Z')

        try:
            query = self.ds_client.query(kind=properties['kind'])
            for key in properties['filters']:
                query.add_filter(key, '=', properties['filters'][key])

            if 'time_field' in properties:
                query.add_filter(properties['time_field'], '>=', time_delta)
                query.order = ['-{}'.format(properties['time_field'])]

            return list(query.fetch())
        except (exceptions.InvalidArgument,
                exceptions.FailedPrecondition) as e:
            logging.error(str(e))
            return None


def format_data(data, key):
    if key in data:
        message_object = data[key]
        return try_loading_string(message_object)

    return None


def try_loading_string(string):
    new_object = None
    try:
        new_object = json.loads(string)
    except json.decoder.JSONDecodeError:
        pass
    return new_object if new_object else string


def validate_dict_keys(keys, input_dict):
    getter = itemgetter(*keys)
    try:
        getter(input_dict)
    except KeyError as e:
        logging.error("Missing {} in dictionary {}".format(e, input_dict))
        return False
    return True


def error_to_notification(request):
    logging.getLogger().setLevel(logging.INFO)
    if request.method == 'POST' and request.args and \
            "interval" in request.args and \
            hasattr(config, 'NOTIFICATION_CONFIG'):
        for notification in config.NOTIFICATION_CONFIG:
            if not validate_dict_keys(
                    ("active", "id", "message_field", "notification"),
                    notification):
                continue
            elif not notification['active']:
                logging.info('Current notification is disabled')
                continue

            data_object = None

            if 'datastore' in notification:
                data_object = Datastore().retrieve_data(
                    notification['datastore'], request.args['interval'])

            logging.info("Found {} errors for notification '{}'".format(
                len(data_object), notification['id']))

            if not data_object:
                continue
            else:
                for row in data_object:
                    data_object = format_data(
                        row, notification['message_field'])

                    if not data_object:
                        continue
                    else:
                        Notification().process(data_object)


if __name__ == '__main__':
    mock_request = requests.session()
    mock_request.method = "POST"
    mock_request.args = {
        "interval": 60
    }

    error_to_notification(mock_request)
