import config

import connexion
import six

from flask import jsonify
from flask import make_response

from google.cloud import datastore

from openapi_server.models.build_status import BuildStatus  # noqa: E501
from openapi_server import util


def build_statuses_get():  # noqa: E501
    """Get all build statuses

    Get a list of all build statuses # noqa: E501


    :rtype: List[BuildStatus]
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


def build_statuses_branch_branch_get(branch):  # noqa: E501
    """Get all branch build statuses

    Get a list of all build statuses from a specific branch # noqa: E501

    :param branch: A unique branch identifier
    :type branch: str

    :rtype: List[BuildStatus]
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


def build_statuses_project_project_id_get(project_id, branch=None):  # noqa: E501
    """Get all project build statuses

    Get a list of all build statuses from a specific project # noqa: E501

    :param project_id: A unique project identifier
    :type project_id: str
    :param branch: A specific branch
    :type branch: str

    :rtype: List[BuildStatus]
    """
    if branch:
        branches = ['master', 'develop']
        if branch not in branches:
            return make_response(jsonify('Branch not of correct type'), 404)

    # Get entity from kind
    db_client = datastore.Client()
    query = db_client.query(kind='CloudBuilds')
    query.add_filter('project_id', '=', project_id)

    if branch:
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
