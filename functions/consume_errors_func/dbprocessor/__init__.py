import datetime
import uuid
import config

from google.cloud import datastore


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        entity_key = self.client.key(config.DB_ERROR_REPORTING_KIND,
                                     str(uuid.uuid4()))
        entity = self.client.get(entity_key)

        payload['project_id'] = ''

        if 'logName' in payload:
            payload['project_id'] = payload['logName'].split('/')[1]
        elif 'resource' in payload \
            and 'labels' in payload['resource'] \
                and 'project_id' in payload['resource']['labels']:
            payload['project_id'] = \
                payload['resource']['labels']['project_id']

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        self.populate_from_payload(entity, payload)
        self.client.put(entity)

        self.populate_count_from_payload(self, payload)

    @staticmethod
    def populate_from_payload(entity, payload):
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

    @staticmethod
    def populate_count_from_payload(self, payload):
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
            self.client.put(error_count)
        else:
            error_count = datastore.Entity(key=error_count_key)
            error_count.update({
                'count': 1,
                'date': datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                'project_id': payload['project_id'],
                'updated': datetime.datetime.utcnow().strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ")
            })
            self.client.put(error_count)
