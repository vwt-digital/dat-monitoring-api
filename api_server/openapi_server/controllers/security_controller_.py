import os

from google.cloud import secretmanager_v1


def get_secret():

    client = secretmanager_v1.SecretManagerServiceClient()

    secret_name = client.secret_version_path(
        os.environ['GOOGLE_CLOUD_PROJECT'],
        '{}-api-key'.format(os.environ['GOOGLE_CLOUD_PROJECT']),
        'latest')

    response = client.access_secret_version(request={"name": secret_name})
    payload = response.payload.data.decode('utf-8').replace('\n', '')

    return payload


decrypted_apikey = None
decrypted_apikey = get_secret()


def info_from_ApiKeyAuth(api_key, required_scopes):
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :param required_scopes Always None. Used for other authentication method
    :type required_scopes: None
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """

    if decrypted_apikey is not None and api_key == decrypted_apikey:
        return {'uid': 'monitoring'}

    return None
