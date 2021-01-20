import datetime
import uuid
import json
import random

import config
from google.cloud import datastore
from google.api_core import exceptions as gcp_exceptions
from retry.api import retry_call


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()

    def process(self, payload):
        entity_key_name = str(uuid.uuid4())
        if 'trace' in payload:
            entity_key_name = payload['trace'].split('/')[-1]
        elif 'insert_id' in payload:
            entity_key_name = payload['insert_id']

        entity_key = self.client.key(config.DB_ERROR_REPORTING_KIND, entity_key_name)
        entity = self.client.get(entity_key)

        if entity:
            print('Trace already exists')
        else:
            entity = datastore.Entity(key=entity_key)

            payload['project_id'] = ''

            if 'logName' in payload:
                payload['project_id'] = payload['logName'].split('/')[1]
            elif 'resource' in payload \
                    and 'labels' in payload['resource'] \
                    and 'project_id' in payload['resource']['labels']:
                payload['project_id'] = payload['resource']['labels']['project_id']

            retry_call(
                self.populate_data, fargs=[entity, payload, entity_key_name], exceptions=gcp_exceptions.Aborted,
                tries=10, delay=random.randint(2, 5), jitter=(1, 5), logger=None)  # nosec

    def populate_data(self, entity, payload, entity_key_name):
        error_key_name = '{}_{}'.format(payload['project_id'], datetime.datetime.utcnow().strftime("%Y-%m-%d"))

        with self.client.transaction():
            self.populate_from_payload(self, entity, payload)
            self.populate_count_from_payload(self, payload, entity_key_name, error_key_name)

    @staticmethod
    def populate_from_payload(self, entity, payload):
        text_payload = ''
        if 'textPayload' in payload:
            try:
                text_payload = json.loads(payload['textPayload'])
            except ValueError:
                pass
            else:
                text_payload = payload['textPayload']

        entity.update({
            'insert_id': payload['insertId'] if 'insertId' in payload else '',
            'project_id': payload['project_id'],
            'log_name': payload['logName'] if 'logName' in payload else '',
            'receive_timestamp': payload['receiveTimestamp'] if 'receiveTimestamp' in payload else
            datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'resource': payload['resource'] if 'resource' in payload else '',
            'labels': payload['labels'] if 'labels' in payload else '',
            'trace': payload['trace'] if 'trace' in payload else '',
            'severity': payload['severity'] if 'severity' in payload else '',
            'text_payload': text_payload
        })
        self.client.put(entity)

    @staticmethod
    def populate_count_from_payload(self, payload, entity_key_name, error_key_name):
        error_count_key = self.client.key(config.DB_ERROR_COUNT_KIND, error_key_name)
        error_count = self.client.get(error_count_key)

        if error_count:
            error_count['count'] += 1
            error_count['updated'] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            error_count['latest_errorreporting_key'] = entity_key_name

            self.client.put(error_count)
        else:
            error_count = datastore.Entity(key=error_count_key)
            error_count.update({
                'count': 1,
                'date': datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                'latest_errorreporting_key': entity_key_name,
                'project_id': payload['project_id'],
                'updated': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            })
            self.client.put(error_count)


if __name__ == '__main__':
    with open('payload.json', 'r') as json_file:
        in_payload = json.load(json_file)
        DBProcessor().process(in_payload)
