from google.cloud import datastore
import config

class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        entity_key = self.client.key(config.DB_ERROR_REPORTING_KIND, payload['id'])
        entity = self.client.get(entity_key)

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        entity.update(payload)
        self.client.put(entity)
