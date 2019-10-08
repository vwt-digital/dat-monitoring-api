from google.cloud import datastore
import config
import uuid
import datetime

class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        key = payload['insertId'] if 'insertId' in payload else str(uuid.uuid4())

        entity_key = self.client.key(config.DB_ERROR_REPORTING_KIND, key)
        entity = self.client.get(entity_key)

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        self.populate_from_payload(entity, payload)
        self.client.put(entity)

    @staticmethod
    def populate_from_payload(entity, payload):
        entity.update({
            'insertId': payload['insertId'] if 'insertId' in payload else '',
            'logName': payload['logName'] if 'logName' in payload else '',
            'receiveTimestamp': payload['receiveTimestamp'] if 'receiveTimestamp' in payload else datetime.datetime.utcnow(),
            'resource': payload['resource'] if 'resource' in payload else '',
            'trace': payload['trace'] if 'trace' in payload else ''
        })
