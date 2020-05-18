from google.cloud import datastore
import config
import datetime
import json
import logging


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
                'projectId' in payload and \
                'REPO_NAME' in payload.get('substitutions', {}) and \
                'BRANCH_NAME' in payload.get('substitutions', {}):

            # Set some variables
            project_id = payload['projectId']
            repo_name = payload['substitutions']['REPO_NAME']
            branch = payload['substitutions']['BRANCH_NAME']
            new_status = parse_status(payload)

            # Create Datastore entity
            key = '{}_{}_{}'.format(project_id, repo_name, branch)
            entity_key = self.client.key(config.DB_BUILD_TRIGGERS_KIND, key)
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)

            old_status = entity.get('status', 'N/A')  # Get old status

            # Update status
            entity.update({
                'repo_name': repo_name,
                'project_id': project_id,
                'branch': branch,
                'status': new_status,
                'updated': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'log_url': payload.get('logUrl', '')
            })

            self.client.put(entity)
            logging.info(f"Build '{key}' changed status from '{old_status}' to '{new_status}'")

            self.remove_old_entity(repo_name, branch)  # Delete old entities after changing key format
        else:
            # Check if the backup executing command is in payload
            payload_dump = json.dumps(payload)
            if 'dcat-deploy/backup/run_backup.sh' in payload_dump and 'id' in payload:
                entity_key = self.client.key(config.DB_BUILD_STATUSES_KIND, payload['id'])
                entity = self.client.get(entity_key)

                if entity is None:
                    entity = datastore.Entity(key=entity_key)

                new_status = parse_status(payload) if 'status' in payload else ''  # Parse status

                entity.update({
                    'id': payload.get('id', ''),
                    'log_url': payload.get('logUrl', ''),
                    'logs_bucket': payload.get('logsBucket', ''),
                    'project_id': payload.get('projectId', ''),
                    'status': new_status,
                    'create_time': payload.get('createTime', ''),
                    'finish_time': payload.get('finishTime', ''),
                    'start_time': payload.get('startTime', '')
                })
                self.client.put(entity)
                logging.info(
                    f"Added new backup build '{payload['id']}' for project '{payload.get('projectId', 'N/A')}'")
            else:
                logging.info("Payload does not contain correct fields, build has not been processed")

    def remove_old_entity(self, repo_name, branch):  # Delete old entities after changing key format
        entity_key = self.client.key(config.DB_BUILD_TRIGGERS_KIND, f"{repo_name}_{branch}")
        self.client.delete(entity_key)
