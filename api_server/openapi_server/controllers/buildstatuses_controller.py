import connexion
import six

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
    query = db_client.query(kind='CloudBuilds')
    db_data = query.fetch()

    # Return results
    if db_data:
        result = [{
            'branch': ap['branch'],
            'git_source': ap['git_source'],
            'organization': ap['organization'],
            'project_id': ap['project_id'],
            'repo_name': ap['repo_name'],
            'status': ap['status'],
            'updated': ap['updated']
        } for ap in db_data]
        return result

    return make_response(jsonify([]), 204)


def build_statuses_triggers_branch_branch_get(branch):  # noqa: E501
    """Get all build trigger statuses by branch

    Get a list of all build trigger statuses from a specific branch # noqa: E501

    :param branch: A unique branch identifier
    :type branch: str

    :rtype: List[BuildTriggerStatus]
    """
    branches = ['master', 'develop']
    if branch in branches:
        # Get entity from kind
        db_client = datastore.Client()
        query = db_client.query(kind='CloudBuilds')
        query.add_filter('branch', '=', branch)
        db_data = query.fetch()

        # Return results
        if db_data:
            result = [{
                'branch': ap['branch'],
                'git_source': ap['git_source'],
                'organization': ap['organization'],
                'project_id': ap['project_id'],
                'repo_name': ap['repo_name'],
                'status': ap['status'],
                'updated': ap['updated']
            } for ap in db_data]
            return result

        return make_response(jsonify([]), 204)

    return make_response(jsonify('Branch not of correct type'), 404)


def build_statuses_other_get():  # noqa: E501
    """Get all other build statuses

    Get a list of all other build statuses # noqa: E501


    :rtype: List[BuildOtherStatus]
    """
    db_client = datastore.Client()
    query = db_client.query(kind='CloudBuildsOther')
    db_data = query.fetch()

    # Return results
    if db_data:
        result = [{
            'finish_time': ap['finishTime'] if 'finishTime' in ap else '',
            'start_time': ap['startTime'] if 'startTime' in ap else '',
            'id': ap['id'] if 'id' in ap else '',
            'project_id': ap['projectId'] if 'projectId' in ap else '',
            'status': ap['status'] if 'status' in ap else ''
        } for ap in db_data]
        return result

    return make_response(jsonify([]), 204)


def build_statuses_other_status_get(status):  # noqa: E501
    """Get all other build statuses by status

    Get a list of all other build statuses with a specific status # noqa: E501

    :param status: A unique status identifier
    :type status: str

    :rtype: List[BuildOtherStatus]
    """
    statuses = ['failing', 'pending', 'passing']
    if status in statuses:
        db_client = datastore.Client()
        query = db_client.query(kind='CloudBuildsOther')
        query.add_filter('status', '=', status)
        db_data = query.fetch()

        # Return results
        if db_data:
            result = [{
                'finish_time': ap['finishTime'] if 'finishTime' in ap else '',
                'start_time': ap['startTime'] if 'startTime' in ap else '',
                'id': ap['id'] if 'id' in ap else '',
                'project_id': ap['projectId'] if 'projectId' in ap else '',
                'status': ap['status'] if 'status' in ap else ''
            } for ap in db_data]
            return result

        return make_response(jsonify([]), 204)

    return make_response(jsonify('Status not of correct type'), 404)
