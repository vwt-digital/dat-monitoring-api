import config
import sys
import os
import json
import base64
import logging
import requests
import datetime
import googleapiclient.discovery
import airspeed

from operator import itemgetter
from google.api_core import exceptions
from google.cloud import datastore
from google.cloud import kms_v1
from google.oauth2 import service_account
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Notification(object):
    def __init__(self):
        pass

    def process(self, message, properties):
        body = None

        if isinstance(message, dict):
            body = self.create_message_from_dict(message)
        elif isinstance(message, str):
            body = self.create_message_from_str(message)

        return body

    def send_notification(self, body, properties):
        if 'type' in properties and properties['type'] == 'mail':
            GmailClient().send_mail(body, properties)
        else:
            logging.error('No notification type found')

    def create_message_from_dict(self, message):
        sections = []
        for section_key in message:
            fields = message[section_key]

            for key in fields:
                if isinstance(fields[key], dict):
                    fields[key] = ', '.join(fields[key])
                elif not fields[key]:
                    fields[key] = '-'

            sections.append({
                "title": section_key.capitalize(),
                "fields": fields
            })

        return {
            "type": "dict",
            "sections": sections
        }

    def create_message_from_str(self, message):
        return {
            "type": "str",
            "message": message
        }


class GmailClient(object):
    def __init__(self):
        if not hasattr(config, 'MAIL_SUBJECT_ADDRESS') or not hasattr(config, 'MAIL_SENDER_ADDRESS'):
            logging.error("Mail configuration missing")
            sys.exit(1)

        kms_client = kms_v1.KeyManagementServiceClient()
        pk_passphrase = kms_client.crypto_key_path_path(os.environ["GCP_PROJECT"], "europe",
                                                        os.environ["GCP_PROJECT"] + "-keyring", "gmail-sdk-key")
        decrypt_response = kms_client.decrypt(pk_passphrase, open(f"gmailsdk_credentials.enc", "rb").read())

        gmailsdk_credentials = decrypt_response.plaintext.decode("utf-8").replace("\n", "")

        delegated_credentials = service_account.Credentials.from_service_account_info(
            json.loads(gmailsdk_credentials), scopes=["https://www.googleapis.com/auth/gmail.send"],
            subject=config.MAIL_SUBJECT_ADDRESS)

        self.gmail_service = googleapiclient.discovery.build("gmail", "v1", credentials=delegated_credentials,
                                                             cache_discovery=False)
        self.subject_address = config.MAIL_SUBJECT_ADDRESS
        self.sender_address = config.MAIL_SENDER_ADDRESS

    def generate_body(self, context):
        try:
            with open("gmail_template.html", "r") as mail_template:
                template_html = mail_template.read()
                mail_template.close()
        except FileNotFoundError:
            logging.error('Mail template file not found')
            return False

        template = airspeed.Template(template_html)
        template_html = template.merge(locals())

        return template_html

    def send_mail(self, message, properties):
        body = self.create_mail(message, properties)

        if body:
            try:
                self.gmail_service.users().messages().send(userId=self.subject_address, body=body).execute()
            except Exception as e:
                logging.error('Mail not send because of exception: {}'.format(str(e)))
                pass

    def create_mail(self, message, properties):
        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender_address
        msg["Subject"] = properties["title"]
        msg["Reply-To"] = self.subject_address
        msg["To"] = properties["receiver"]

        mail_body = self.generate_body(message)
        if not mail_body:
            return False

        msg.attach(MIMEText(mail_body, "html"))
        raw = base64.urlsafe_b64encode(msg.as_bytes())
        raw = raw.decode()
        return {"raw": raw}


class Datastore(object):
    def __init__(self):
        self.ds_client = datastore.Client()

    def retrieve_data(self, properties, interval=60):
        if not validate_dict_keys(("kind", "filters"), properties):
            return None
        elif len(properties['filters']) <= 0:
            logging.error('No filters found for this notification')
            return None

        time_delta = (datetime.datetime.utcnow() - datetime.timedelta(minutes=interval)).strftime(
            '%Y-%m-%dT%H:00:00.000000000Z')

        try:
            query = self.ds_client.query(kind=properties['kind'])
            for key in properties['filters']:
                query.add_filter(key, '=', properties['filters'][key])

            if 'time_field' in properties:
                query.add_filter(properties['time_field'], '>=', time_delta)
                query.order = ['-{}'.format(properties['time_field'])]

            return list(query.fetch())
        except (exceptions.InvalidArgument, exceptions.FailedPrecondition) as e:
            logging.error(str(e))
            return None


def format_data(data, key):
    if key in data:
        new_object = None
        try:
            new_object = json.loads(data[key])
        except json.decoder.JSONDecodeError:
            pass
        return new_object if new_object else data[key]
    return None


def validate_dict_keys(keys, input_dict):
    getter = itemgetter(*keys)
    try:
        getter(input_dict)
    except KeyError as e:
        logging.error("Missing {} in dictionary {}".format(e, input_dict))
        return False
    return True


def error_to_notification(request):
    logging.getLogger().setLevel(logging.INFO)
    if request.method == 'POST' and request.args and "interval" in request.args and \
            hasattr(config, 'NOTIFICATION_CONFIG'):
        for notification in config.NOTIFICATION_CONFIG:
            if not validate_dict_keys(("active", "id", "message_field", "database", "notification"), notification):
                continue
            elif not notification['active']:
                logging.info('Current notification is disabled')
                continue
            elif 'type' not in notification['database']:
                logging.error('No database type is specified')
                continue

            data_object = None

            if notification['database']['type'] == 'datastore':
                data_object = Datastore().retrieve_data(notification['database'], request.args['interval'])

            logging.info("Found {} errors for notification '{}'".format(len(data_object), notification['id']))

            if not data_object:
                continue
            else:
                data_object_list = {
                    'title': notification['notification'].get('title', 'Error notification'),
                    'content': []
                }

                for row in data_object:
                    data_object = format_data(row, notification['message_field'])

                    if not data_object:
                        continue

                    body = Notification().process(data_object, notification['notification'])
                    data_object_list['content'].append(body)

                Notification().send_notification(data_object_list, notification['notification'])


if __name__ == '__main__':
    mock_request = requests.session()
    mock_request.method = "POST"
    mock_request.args = {
        "interval": 60
    }

    error_to_notification(mock_request)
