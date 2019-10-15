import connexion
import six
import config
import datetime
import time

from flask import jsonify
from flask import make_response

from google.cloud import datastore

from openapi_server.models.error_report import ErrorReport  # noqa: E501
from openapi_server.models.error_report_count import ErrorReportCount  # noqa: E501
from openapi_server import util


def error_reporting_get(days=None, max_rows=None):  # noqa: E501
    """Get errors reportings by conditions

    Get a list of errors reportings by days and max rows # noqa: E501

    :param days: Total days to include
    :type days: int
    :param max_rows: Max rows to return
    :type max_rows: int

    :rtype: List[ErrorReport]
    """
    max_rows = max_rows if max_rows else 20
    days = days if days else 7

    time_delta = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_REPORTING_KIND)
    query.add_filter('receiveTimestamp', '>', time_delta)
    query.order = ['-receiveTimestamp']
    db_data = query.fetch(max_rows)

    # Return results
    if db_data:
        result = [{
            'id': ap['insertId'],
            'log_name': ap['logName'],
            'receive_timestamp': ap['receiveTimestamp'],
            'resource': ap['resource'],
            'trace': ap['trace']
        } for ap in db_data]
        return result

    return make_response(jsonify([]), 204)


def error_reporting_count_get():  # noqa: E501
    """Get count of project errors reportings in last 7 days

    Get a list of projects with errors reportings count in last 7 days # noqa: E501


    :rtype: List[ErrorReportCount]
    """
    time_delta = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_REPORTING_KIND)
    query.add_filter('receiveTimestamp', '>', time_delta)
    query.order = ['-receiveTimestamp']
    db_data = query.fetch()

    # Return results
    if db_data:
        counted_projects = {}
        projects_object = []

        for error in db_data:
            project_id = error['logName'].split('/')[1]
            if project_id in counted_projects:
                counted_projects[project_id]['count'] = counted_projects[project_id]['count'] + 1
            else:
                counted_projects[project_id] = {
                    'project_id': project_id,
                    'count': 1,
                    'latest_updated': error['receiveTimestamp'],
                    'resource': error['resource']
                }

        for value in counted_projects:
            projects_object.append(counted_projects[value])

        return projects_object

    return make_response(jsonify([]), 204)
