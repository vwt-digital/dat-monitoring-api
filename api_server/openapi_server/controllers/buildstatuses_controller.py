import connexion
import six
import config
import datetime

from flask import jsonify
from flask import make_response

from google.cloud import datastore

from openapi_server.models.build_other_status import BuildOtherStatus  # noqa: E501
from openapi_server.models.build_trigger_status import BuildTriggerStatus  # noqa: E501
from openapi_server import util


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
            'branch': status['branch'] if 'branch' in status else '',
            'git_source': status['git_source'] if 'git_source' in status else '',
            'organization': status['organization'] if 'organization' in status else '',
            'project_id': status['project_id'] if 'project_id' in status else '',
            'repo_name': status['repo_name'] if 'repo_name' in status else '',
            'status': status['status'] if 'status' in status else '',
            'updated': status['updated'] if 'updated' in status else '',
            'log_url': status['log_url'] if 'log_url' in status else ''
        } for status in db_data]
        return result

    return make_response(jsonify([]), 204)


def build_statuses_other_get():  # noqa: E501
    """Get last 20 other build statuses

    Get a list of last 20 other build statuses # noqa: E501


    :rtype: List[BuildOtherStatus]
    """
    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_BUILD_STATUSES_KIND)
    query.order = ['-finishTime']
    db_data = query.fetch(20)

    # Return results
    if db_data:
        result = [{
            'finish_time': status['finishTime'] if 'finishTime' in status else '',
            'start_time': status['startTime'] if 'startTime' in status else '',
            'id': status['id'] if 'id' in status else '',
            'project_id': status['projectId'] if 'projectId' in status else '',
            'status': status['status'] if 'status' in status else '',
            'log_url': status['log_url'] if 'log_url' in status else ''
        } for status in db_data]
        return result

    return make_response(jsonify([]), 204)


def build_statuses_other_status_get(status, days=None, max_rows=None):  # noqa: E501
    """Get other build statuses by conditions

    Get a list of other build statuses by status, days and max rows # noqa: E501

    :param status: A unique status identifier
    :type status: str
    :param days: Total days to include
    :type days: int
    :param max_rows: Max rows to return
    :type max_rows: int

    :rtype: List[BuildOtherStatus]
    """
    statuses = ['failing', 'pending', 'passing']

    if status and status not in statuses:
        return make_response(jsonify('Status not of correct type'), 404)

    max_rows = max_rows if max_rows else 20
    days = days if days else 7

    time_delta = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_BUILD_STATUSES_KIND)

    if status:
        query.add_filter('status', '=', status)

    query.add_filter('finishTime', '>', time_delta)
    query.order = ['-finishTime']

    db_data = query.fetch(max_rows)

    # Return results
    if db_data:
        result = [{
            'finish_time': status['finishTime'] if 'finishTime' in status else '',
            'start_time': status['startTime'] if 'startTime' in status else '',
            'id': status['id'] if 'id' in status else '',
            'project_id': status['projectId'] if 'projectId' in status else '',
            'status': status['status'] if 'status' in status else '',
            'log_url': status['logUrl'] if 'logUrl' in status else ''
        } for status in db_data]
        return result

    return make_response(jsonify([]), 204)
