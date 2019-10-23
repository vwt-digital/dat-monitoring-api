import config
import datetime

from flask import jsonify
from flask import make_response

from google.cloud import datastore


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
    query.add_filter('receive_timestamp', '>', time_delta)
    query.order = ['-receive_timestamp']
    db_data = query.fetch(max_rows)

    # Return results
    if db_data:
        result = [{
            'id': ap['insert_id'],
            'log_name': ap['log_name'],
            'project_id': ap['project_id'],
            'receive_timestamp': ap['receive_timestamp'],
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
    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_REPORTING_KIND)
    query.distinct_on = ['receive_timestamp', 'project_id', 'resource.type']
    query.order = ['-receive_timestamp', 'project_id', 'resource.type']
    db_data = query.fetch(5)

    # Return results
    if db_data:
        result = [{
            'id': error['insert_id'],
            'log_name': error['log_name'],
            'project_id': error['project_id'],
            'receive_timestamp': error['receive_timestamp'],
            'resource': error['resource'],
            'trace': error['trace'],
            'count': '{}'.format(get_project_error_count(
                error['project_id']))
        } for error in db_data]
        return result
    return make_response(jsonify([]), 204)


def get_project_error_count(project_id):
    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_COUNT_KIND)
    query.add_filter('project_id', '=', project_id)
    db_data = query.fetch(7)

    total_count = 0
    if db_data:
        for error_count in db_data:
            total_count = total_count + error_count['count']

    return total_count
