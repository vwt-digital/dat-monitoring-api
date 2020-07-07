import config
import os
import datetime
import itertools
import base64
import operator
import numpy as np

from flask import jsonify
from flask import make_response

from functools import reduce
from google.cloud import datastore, kms


def kms_encrypt_decrypt_cursor(cursor, type):
    if cursor:
        project_id = os.environ['GOOGLE_CLOUD_PROJECT']
        location_id = "europe"
        key_ring_id = f"{project_id}-keyring"
        crypto_key_id = "db-cursor-key"

        client = kms.KeyManagementServiceClient()
        name = client.crypto_key_path_path(project_id, location_id, key_ring_id, crypto_key_id)

        if type == 'encrypt':
            encrypt_response = client.encrypt(name, cursor.encode())
            response = base64.urlsafe_b64encode(encrypt_response.ciphertext).decode()
        else:
            encrypt_response = client.decrypt(name, base64.urlsafe_b64decode(cursor))
            response = encrypt_response.plaintext
    else:
        response = None

    return response


def error_reports_get(page_size=50, cursor=None, page='Next'):  # noqa: E501
    """Get errors reportings

    Get a list of errors reportings # noqa: E501

    :param page_size: The numbers of items within a page.
    :type page_size: int
    :param cursor: The query cursor of the page
    :type cursor: str
    :param page: Selector to get next or previous page based on the cursor
    :type page: str

    :rtype: List[ErrorReportResponse]
    """

    if page == 'prev' and not cursor:
        return make_response(jsonify('A cursor is required when requesting a previous page.'), 400)

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_ERROR_REPORTING_KIND)

    query_params = {
        'limit': page_size,
        'start_cursor': kms_encrypt_decrypt_cursor(cursor, 'decrypt') if cursor else None
    }

    # When the previous page is requested and the latest cursor from the original query is used
    # to get results in reverse.
    if page == 'prev':
        query.order = ['receive_timestamp', '__key__']
    else:
        query.order = ['-receive_timestamp', '-__key__']

    query_iter = query.fetch(**query_params)  # Execute query

    current_page = next(query_iter.pages)  # Setting current iterator page
    db_data = list(current_page)  # Set page results list

    # Return results
    if db_data:
        result_items = [{
            'id': ap.get('insert_id', ''),
            'labels': ap.get('labels', {}),
            'log_name': ap.get('log_name', ''),
            'project_id': ap.get('project_id', ''),
            'received_at': ap.get('receive_timestamp', ''),
            'resource': ap.get('resource', {}),
            'severity': ap.get('severity', ''),
            'text_payload': ap.get('text_payload', ''),
            'trace': ap.get('trace', ''),
        } for ap in db_data]

        # Sort results if previous page is requested because query sort order is ascending instead of descending
        if page == 'prev':
            results = sorted(result_items, key=lambda i: i['received_at'], reverse=True)
            next_cursor = cursor  # Grab current cursor for next page
        else:
            results = result_items
            next_cursor = query_iter.next_page_token.decode()  # Grab new cursor for next page
    else:
        results = []
        next_cursor = cursor

    # Create response object
    response = {
        'status': 'success',
        'page_size': page_size,
        'next_cursor': kms_encrypt_decrypt_cursor(next_cursor, 'encrypt'),
        'results': results
    }
    return response


def error_reports_counts_get(days=None, max_rows=None):  # noqa: E501
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
            error['received_at'] = error['receive_timestamp']
            del error['receive_timestamp']
            error['count'] = error_reporting_count[error['project_id']]['count'] \
                if error['project_id'] in error_reporting_count else ''

        return sorted(error_list, key=lambda i: i['received_at'],
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


def get_from_dict(data_dict, map_list):
    """Returns a dictionary based on a mapping"""
    return reduce(operator.getitem, map_list, data_dict)


def security_notifications_get(page_size=50, cursor=None, page='Next'):  # noqa: E501
    """Get a list of security notifications

    Get a list of security notifications # noqa: E501

    :param page_size: The numbers of items within a page.
    :type page_size: int
    :param cursor: The query cursor of the page
    :type cursor: str
    :param page: Selector to get next or previous page based on the cursor
    :type page: str

    :rtype: List[SecurityNotificationResponse]
    """

    if page == 'prev' and not cursor:
        return make_response(jsonify('A cursor is required when requesting a previous page.'), 400)

    db_client = datastore.Client()
    query = db_client.query(kind=config.DB_SCC_NOTIFICATIONS_KIND)

    query_params = {
        'limit': page_size,
        'start_cursor': kms_encrypt_decrypt_cursor(cursor, 'decrypt') if cursor else None
    }

    # When the previous page is requested and the latest cursor from the original query is used
    # to get results in reverse.
    if page == 'prev':
        query.order = ['updated', '__key__']
    else:
        query.order = ['-updated', '-__key__']

    query_iter = query.fetch(**query_params)  # Execute query

    current_page = next(query_iter.pages)  # Setting current iterator page
    db_data = list(current_page)  # Set page results list

    # Return results
    if db_data:
        result_items = [{
            'category': ap.get('category', ''),
            'created_at': ap.get('created', ''),
            'exception_instructions': get_from_dict(
                ap, ['source', 'finding', 'sourceProperties', 'ExceptionInstructions']),
            'explanation': get_from_dict(ap, ['source', 'finding', 'sourceProperties', 'Explanation']),
            'external_uri': get_from_dict(ap, ['source', 'finding', 'externalUri']),
            'id': ap.key.id_or_name,
            'project_id': ap.get('project_id', ''),
            'recommendation': ap.get('recommendation', ''),
            'resource_name': get_from_dict(ap, ['source', 'finding', 'resourceName']),
            'severity': get_from_dict(ap, ['source', 'finding', 'sourceProperties', 'SeverityLevel']),
            'updated_at': ap.get('updated', ''),
        } for ap in db_data]

        # Sort results if previous page is requested because query sort order is ascending instead of descending
        if page == 'prev':
            results = sorted(result_items, key=lambda i: i['updated_at'], reverse=True)
            next_cursor = cursor  # Grab current cursor for next page
        else:
            results = result_items
            next_cursor = query_iter.next_page_token.decode() if query_iter.next_page_token else None  # Grab new cursor for next page
    else:
        results = []
        next_cursor = cursor

    # Create response object
    response = {
        'status': 'success',
        'page_size': page_size,
        'next_cursor': kms_encrypt_decrypt_cursor(next_cursor, 'encrypt'),
        'results': results
    }
    return response
