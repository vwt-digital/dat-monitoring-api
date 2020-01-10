from google.cloud import datastore
import config
import datetime
import json


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
            'substitutions' in payload and \
            'REPO_NAME' in payload['substitutions'] and \
                'BRANCH_NAME' in payload['substitutions']:

            repo_name = payload['substitutions'].get('REPO_NAME')
            branch = payload['substitutions'].get('BRANCH_NAME')
            kind = config.DB_BUILD_TRIGGERS_KIND

            key = '{}_{}'.format(repo_name, branch)
            entity_key = self.client.key(kind, key)
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)

            self.populate_trigger_from_payload(entity, payload)
            self.client.put(entity)
        elif 'id' in payload:
            # Check if the backup executing command is in payload
            payload_dump = json.dumps(payload)
            if 'dcat-deploy/backup/run_backup.sh' in payload_dump:
                kind = config.DB_BUILD_STATUSES_KIND

                entity_key = self.client.key(kind, payload['id'])
                entity = self.client.get(entity_key)

                if entity is None:
                    entity = datastore.Entity(key=entity_key)

                self.populate_other_from_payload(entity, payload)
                self.client.put(entity)

    @staticmethod
    def populate_trigger_from_payload(entity, payload):
        # Set repo and branch name
        repo_name = payload['substitutions'].get('REPO_NAME', 'N/A')
        branch = payload['substitutions'].get('BRANCH_NAME', 'N/A')

        # Set status to either pending, failing or passing
        status = parse_status(payload)

        entity.update({
            'repo_name': repo_name,
            'project_id': payload.get('projectId', ''),
            'branch': branch,
            'status': status,
            'updated': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'log_url': payload.get('logUrl', '')
        })

    @staticmethod
    def populate_other_from_payload(entity, payload):
        # Set status to either pending, failing or passing
        status = parse_status(payload) if 'status' in payload else ''

        entity.update({
            'id': payload.get('id', ''),
            'log_url': payload.get('logUrl', ''),
            'logs_bucket': payload.get('logs_bucket', ''),
            'project_id': payload.get('project_id', ''),
            'status': '{}'.format(status),
            'create_time': payload.get('create_time', ''),
            'finish_time': payload.get('finish_time', ''),
            'start_time': payload.get('start_time', '')
        })
