import os
import io
import json

from google.cloud import kms_v1

def decrypt():
    project_id = os.environ['PROJECT_ID']
    location_id = "europe"
    key_ring_id = "api-key"
    crypto_key_id = "api-key-monitoring"

    # Creates an API client for the KMS API.
    client = kms_v1.KeyManagementServiceClient()

    # The resource name of the CryptoKey.
    name = client.crypto_key_path_path(project_id, location_id, key_ring_id,
                                       crypto_key_id)

    # Use the KMS API to decrypt the data.
    with io.open('api-credentials.enc', "rb") as file:
        c_text = file.read()

    response = client.decrypt(name, c_text)
    secret_dict = response.plaintext.decode("utf-8").replace('\n', '')

    return secret_dict


decrypted_apikey = None
decrypted_apikey = decrypt()


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
