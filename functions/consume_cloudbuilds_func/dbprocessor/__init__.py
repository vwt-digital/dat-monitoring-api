from google.cloud import datastore
import config
import os
import uuid
import datetime

def parse_status(payload):
    status = 'pending'
    if payload['status'] == 'QUEUED' or payload['status'] == 'WORKING':
        status = 'pending'
    if payload['status'] in ['FAILURE', 'TIMEOUT', 'CANCELLED']:
        status = 'failing'
    if payload['status'] == 'SUCCESS':
        status = 'passing'

    return status


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()
        pass

    def process(self, payload):
        if 'status' in payload and \
            'source' in payload and \
            'repoSource' in payload['source'] and \
            'repoName' in payload['source']['repoSource'] and \
            'branchName' in payload['source']['repoSource']:

            repo_name = payload['source']['repoSource'].get('repoName')
            branch = payload['source']['repoSource'].get('branchName')
            kind = config.DB_BUILD_TRIGGERS_KIND

            key = '{}_{}'.format(repo_name, branch)
            entity_key = self.client.key(kind, key)
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)

            self.populate_trigger_from_payload(entity, payload)
            self.client.put(entity)
        elif 'id' in payload:
            kind = config.DB_BUILD_STATUSES_KIND

            entity_key = self.client.key(kind, payload['id'])
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)

            self.populate_other_from_payload(entity, payload)
            self.client.put(entity)

    @staticmethod
    def populate_trigger_from_payload(entity, payload):
        # Set repo and branch names | repoName = {git_source}_{organization}_{project_id}
        repo_name = payload['source']['repoSource'].get('repoName')
        branch = payload['source']['repoSource'].get('branchName')

        # Set status to either pending, failing or passing
        status = parse_status(payload)

        entity.update({
            'git_source': repo_name.split('_')[0],
            'organization': repo_name.split('_')[1],
            'repo_name': repo_name.split('_')[2],
            'project_id': payload['projectId'],
            'branch': branch,
            'status': status,
            'updated': datetime.datetime.utcnow()
        })

    @staticmethod
    def populate_other_from_payload(entity, payload):
        # Set status to either pending, failing or passing
        status = parse_status(payload) if 'status' in payload else '';

        entity.update({
            'id': payload['id'],
            'logUrl': payload['logUrl'] if 'logUrl' in payload else '',
            'logsBucket': payload['logsBucket'] if 'logsBucket' in payload else '',
            'projectId': payload['projectId'] if 'projectId' in payload else '',
            'status': '{}'.format(status),
            'createTime': payload['createTime'] if 'createTime' in payload else '',
            'finishTime': payload['finishTime'] if 'finishTime' in payload else '',
            'startTime': payload['startTime'] if 'startTime' in payload else ''
        })
