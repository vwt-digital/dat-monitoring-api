from google.cloud import datastore
import config
import os
import uuid
import datetime


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        kind = os.environ.get('DB_PROCESSOR_KIND', 'Required parameter is missed')
        entity_key = self.client.key(kind, str(uuid.uuid4()))
        entity = self.client.get(entity_key)

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        self.populate_from_payload(entity, payload)
        self.client.put(entity)

    @staticmethod
    def populate_from_payload(entity, payload):
        if 'status' in payload and 'source' in payload and 'repoSource' in payload['source']:
            # Set repo and branch names | repoName = {git_source}_{organization}_{project_id}
            repo_name = payload['source']['repoSource'].get('repoName', str(uuid.uuid4()))
            branch = payload['source']['repoSource'].get('branchName','')

            # Set status to either pending, failing or passing
            status = 'pending'
            if payload['status'] == 'QUEUED' or payload['status'] == 'WORKING':
                status = 'pending'
            if payload['status'] in ['FAILURE', 'TIMEOUT']:
                status = 'failing'
            if payload['status'] == 'SUCCESS':
                status = 'passing'

            entity.update({
                'git_source': repo_name.split('_')[0],
                'organization': repo_name.split('_')[1],
                'project_id': repo_name.split('_')[2],
                'branch': branch,
                'status': status,
                'updated': datetime.datetime.utcnow()
            })
