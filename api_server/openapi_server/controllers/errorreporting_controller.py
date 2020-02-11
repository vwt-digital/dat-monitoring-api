import config
import datetime
import itertools
import numpy as np

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


def error_reporting_count_get(days=None, max_rows=None):  # noqa: E501
    """Get count of project errors reportings in last x days

    Get a list of projects with errors reportings count in last x days # noqa: E501

    :param days: Total days to include
    :type days: int
    :param max_rows: Max rows to return
    :type max_rows: int

    :rtype: List[ErrorReportCount]
    """

    if days < 1 or max_rows < 1:
        return make_response(
            jsonify("Parameters must be more than 0"), 403)

    time_delta = (datetime.datetime.utcnow() - datetime.timedelta(
        days=days)).strftime('%Y-%m-%d')

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_COUNT_KIND)
    query.add_filter('date', '>=', time_delta)
    query.distinct_on = ['date', 'updated', 'project_id']
    query.order = ['-date', '-updated', 'project_id']
    db_data = query.fetch()

    if db_data:
        error_reporting_count = {}
        error_reporting_keys = []

        for error_count in db_data:
            project_id = error_count['project_id']

            if 'count' in error_count:
                if project_id in error_reporting_count:
                    error_reporting_count[project_id]['count'] = \
                        error_reporting_count[project_id]['count'] + \
                        error_count['count']
                else:
                    error_reporting_count[project_id] = {
                        'count': error_count['count'],
                        'latest_errorreporting_key': error_count['latest_errorreporting_key']
                    }

        for key in itertools.islice(error_reporting_count, max_rows):
            if 'latest_errorreporting_key' in error_reporting_count[key]:
                error_reporting_keys.append(
                    error_reporting_count[key]['latest_errorreporting_key'])

        error_list = get_latest_error(error_reporting_keys, db_client)

        for error in error_list:
            error['count'] = error_reporting_count[error['project_id']]['count'] \
                if error['project_id'] in error_reporting_count else ''

        return sorted(error_list, key=lambda i: i['receive_timestamp'],
                      reverse=True)
    return make_response(jsonify([]), 204)


def get_latest_error(keys, db_client):
    error_keys = []
    for chunk in np.array_split(keys, 500):
        error_batch_keys = []
        for key in chunk:
            error_batch_keys.append(
                db_client.key(config.DB_ERROR_REPORTING_KIND, key))
        error_keys = error_keys + db_client.get_multi(error_batch_keys)

    return error_keys
