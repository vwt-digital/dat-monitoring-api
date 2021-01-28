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

    def process(self, payload):
        payload_dump = json.dumps(payload)
        correct_build = False
        repo_name = None
        branch = None

        if 'status' in payload and 'id' in payload and 'projectId' in payload:
            if 'REPO_NAME' in payload.get('substitutions', {}) and 'BRANCH_NAME' in payload.get('substitutions', {}):
                correct_build = True
                repo_name = payload['substitutions']['REPO_NAME']
                branch = payload['substitutions']['BRANCH_NAME']
            elif 'dcat-deploy/backup/run_backup.sh' in payload_dump and \
                    '_BRANCH_NAME' in payload.get('substitutions', {}):
                correct_build = True
                repo_name = 'backup'
                branch = payload['substitutions']['_BRANCH_NAME']
            elif 'python3 aggregate.py -c data_catalog.json' in payload_dump and \
                    '_BRANCH_NAME' in payload.get('substitutions', {}):
                correct_build = True
                repo_name = 'backup_aggregation'
                branch = payload['substitutions']['_BRANCH_NAME']

        if correct_build:
            # Set some variables
            build_id = payload['id']
            project_id = payload['projectId']
            new_status = parse_status(payload)
            new_status_original = payload['status']

            # Create Datastore entity
            key = '{}_{}_{}'.format(project_id, repo_name, branch)
            entity_key = self.client.key(config.DB_BUILD_TRIGGERS_KIND, key)
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)

            old_build_id = entity.get('build_id', None)  # Get old build id
            old_status = entity.get('status', 'N/A')  # Get old status
            old_status_original = entity.get('status_original', 'N/A')  # Get old original status

            if old_build_id and build_id == old_build_id and \
                    new_status == 'pending' and old_status in ['failing', 'passing']:
                new_status = old_status
                new_status_original = old_status_original

            # Update status
            entity.update({
                'repo_name': repo_name,
                'project_id': project_id,
                'branch': branch,
                'status': new_status,
                'status_original': new_status_original,
                'build_id': build_id,
                'updated': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                'log_url': payload.get('logUrl', '')
            })

            self.client.put(entity)
            if old_status != new_status:
                logging.info(f"Build '{key}' changed status from '{old_status}' to '{new_status}'")
            else:
                logging.info(f"Build '{key}' kept status '{old_status}'. " +
                             f"Original status changed from '{old_status_original}' to '{new_status_original}'")

            self.remove_old_entity(repo_name, branch)  # Delete old entities after changing key format
        else:
            logging.info("Payload does not contain correct fields, build has not been processed")

    def remove_old_entity(self, repo_name, branch):  # Delete old entities after changing key format
        entity_key = self.client.key(config.DB_BUILD_TRIGGERS_KIND, f"{repo_name}_{branch}")
        self.client.delete(entity_key)
