import connexion
import six
import config

from flask import jsonify
from flask import make_response

from google.cloud import datastore

from openapi_server.models.error_report import ErrorReport  # noqa: E501
from openapi_server import util


def error_reporting_get():  # noqa: E501
    """Get last 20 error reportings

    Get a list of last 20 error reportings # noqa: E501


    :rtype: List[ErrorReport]
    """
    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_REPORTING_KIND)
    query.order = ['-receiveTimestamp']
    db_data = query.fetch(20)

    # Return results
    if db_data:
        result = [{
            'id': ap['insertId'] if 'insertId' in ap else '',
            'json_payload': ap['jsonPayload'] if 'jsonPayload' in ap else '',
            'log_name': ap['logName'] if 'logName' in ap else '',
            'receive_timestamp': ap['receiveTimestamp'] if 'receiveTimestamp' in ap else '',
            'resource': ap['resource'] if 'resource' in ap else '',
            'source_location': ap['sourceLocation'] if 'sourceLocation' in ap else '',
            'text_payload': ap['textPayload'] if 'textPayload' in ap else '',
            'trace': ap['trace'] if 'finishTime' in ap else ''
        } for ap in db_data]
        return result

    return make_response(jsonify([]), 204)
