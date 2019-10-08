from google.cloud import datastore
import config
import uuid

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

        entity.update(payload)
        self.client.put(entity)
