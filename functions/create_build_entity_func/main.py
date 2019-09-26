import base64
import os
import json
import uuid
import datetime
from google.cloud import datastore

def create_build_entity_func(data, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         data (dict): The dictionary with data specific to this type of event.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata.
    """

    if 'data' in data:
        strdecoded = base64.b64decode(data['data']).decode('utf-8')
        buildstatusmessage = json.loads(strdecoded)
        print(buildstatusmessage)

        if 'status' in buildstatusmessage and 'source' in buildstatusmessage and 'repoSource' in buildstatusmessage['source']:
            # Set repo and branch names | repoName = {git_source}_{organization}_{project_id}
            repo_name = buildstatusmessage['source']['repoSource'].get('repoName', str(uuid.uuid4()))
            branch = buildstatusmessage['source']['repoSource'].get('branchName','')

            # Set status to either pending, failing or passing
            status = 'pending'
            if buildstatusmessage['status'] == 'QUEUED' or buildstatusmessage['status'] == 'WORKING':
                status = 'pending'
            if buildstatusmessage['status'] in ['FAILURE', 'TIMEOUT']:
                status = 'failing'
            if buildstatusmessage['status'] == 'SUCCESS':
                status = 'passing'

            # Add entity to datastore kind
            db_client = datastore.Client()
            project_build_key = db_client.key(os.environ['DATASTORE_KIND'], str(uuid.uuid4()))
            project_build_info = datastore.Entity(key=project_build_key)

            project_build_info.update({
                'git_source': repo_name.split('_')[0],
                'organization': repo_name.split('_')[1],
                'project_id': repo_name.split('_')[2],
                'branch': branch,
                'status': status,
                'updated': datetime.datetime.utcnow()
            })
            db_client.put(project_build_info)
