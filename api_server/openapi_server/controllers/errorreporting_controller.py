import connexion
import six
import config
import datetime
import pandas
import json

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
        df = pandas.DataFrame(db_data, columns=['logName', 'receiveTimestamp', 'resource'])
        df['logName'] = df['logName'].str.split('/', expand = True)[1]
        df['count'] = df.groupby('logName').transform('count')[['receiveTimestamp']]
        df = df.sort_values('receiveTimestamp').groupby('logName').apply(lambda x: x.tail(1))
        df = df.sort_values(by='receiveTimestamp', ascending=False)

        df = df.rename(columns={'logName': 'project_id', 'receiveTimestamp': 'latest_updated'})

        df_json = df.to_json(orient="records")
        return json.loads(df_json)

    return make_response(jsonify([]), 204)
