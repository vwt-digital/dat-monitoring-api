import connexion
import six
import config
import datetime

from flask import jsonify
from flask import make_response

from google.cloud import datastore

from openapi_server.models.error_report import ErrorReport  # noqa: E501
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
