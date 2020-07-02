import config

from flask import jsonify
from flask import make_response

from google.cloud import datastore


def build_statuses_triggers_get():  # noqa: E501
    """Get all build trigger statuses

    Get a list of all build trigger statuses # noqa: E501


    :rtype: List[BuildTriggerStatus]
    """
    # Get entity from kind
    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_BUILD_TRIGGERS_KIND)
    query.order = ['-updated']
    db_data = query.fetch()

    # Return results
    if db_data:
        result = [{
            'branch': status.get('branch', ''),
            'project_id': status.get('project_id', ''),
            'repo_name': status.get('repo_name', ''),
            'status': status.get('status', ''),
            'updated_at': status.get('updated', ''),
            'log_url': status.get('log_url', '')
        } for status in db_data]
        return result

    return make_response(jsonify([]), 204)
