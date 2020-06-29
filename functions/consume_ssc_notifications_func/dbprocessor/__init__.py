from google.cloud import datastore
import config
import datetime
import json
import logging


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        # Set some variables
        project_id = payload['finding']['sourceProperties']['ProjectId']
        create_time = payload['finding']['createTime']
        notification_id = payload['finding']['name']
        recommendation = payload['finding']['sourceProperties']['Recommendation']
        catagory = payload['finding']['catagory']

        # print("Project id = : {}".format(project_id))

        # Create Datastore entity
        key = '{}'.format(notification_id)
        entity_key = self.client.key(config.DB_BUILD_TRIGGERS_KIND, key)
        entity = self.client.get(entity_key)

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        # Update status
        entity.update({
            'project_id': project_id,
            'catagory' : catagory,
            'created' : create_time,
            'updated': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'recommendation' : recommendation,
            'source': payload
        })

        self.client.put(entity)
