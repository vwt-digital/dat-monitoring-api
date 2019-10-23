import datetime
import uuid
import config

from google.cloud import datastore


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        entity_key_name = str(uuid.uuid4())
        if 'trace' in payload:
            entity_key_name = payload['trace'].split('/')[-1]

        entity_key = self.client.key(config.DB_ERROR_REPORTING_KIND,
                                     entity_key_name)
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
                payload['project_id'] = \
                    payload['resource']['labels']['project_id']

            self.populate_from_payload(self, entity, payload)
            self.populate_count_from_payload(self, payload, entity_key_name)

    @staticmethod
    def populate_from_payload(self, entity, payload):
        entity.update({
            'insert_id': payload['insertId'] if 'insertId' in payload else '',
            'project_id': payload['project_id'],
            'log_name': payload['logName'] if 'logName' in payload else '',
            'receive_timestamp': payload['receiveTimestamp']
            if 'receiveTimestamp' in payload else
            datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'resource': payload['resource'] if 'resource' in payload else '',
            'trace': payload['trace'] if 'trace' in payload else ''
        })
        self.client.put(entity)

    @staticmethod
    def populate_count_from_payload(self, payload, entity_key_name):
        error_key_name = '{}_{}'.format(payload['project_id'],
                                        datetime.datetime.utcnow()
                                        .strftime("%Y-%m-%d"))

        error_count_key = self.client.key(config.DB_ERROR_COUNT_KIND,
                                          error_key_name)
        error_count = self.client.get(error_count_key)

        if error_count:
            error_count['count'] += 1
            error_count['updated'] = datetime.datetime.utcnow() \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            if entity_key_name not in error_count['error_reporting_keys']:
                error_count['error_reporting_keys'].append(entity_key_name)

            self.client.put(error_count)
        else:
            error_count = datastore.Entity(key=error_count_key)
            error_count.update({
                'count': 1,
                'date': datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                'error_reporting_keys': [entity_key_name],
                'project_id': payload['project_id'],
                'updated': datetime.datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ")
            })
            self.client.put(error_count)
