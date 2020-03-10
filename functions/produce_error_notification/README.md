# Monitoring error notifier
This function creates a notification based on configuration and logging.

## Configuration
This function relies on configuration to send messages based on filters. A [list of notifications](#notification-list-structure) can be specified within the `config.py` (see [config.example.py](config.example.py) for an example) that each has an influence on the outcome. 

The fields required within a notification dictionary are:
- `active` `[boolean]`: this will enable or disable the notification;
- `id` `[string]`: an unique ID that will be used to differentiate logging;
- `message_field` `[string]`: the field that will be send towards the receiver of the notification;
- `database` `[dict]`: a dictionary that specifies the location of the data used for the notification ([see types](#datastore));
- `notification` `[dict]`: a dictionary that contains the necessary fields to send a notification ([see types](#e-mail)).

##### Notification list structure
~~~json
[
  {
    "active": true,
    "id": "an-unique-id",
    "message_field": "field-name",
    "database": {},
    "notification": {}
  },
  {
    "active": false,
    "id": "another-unique-id",
    "message_field": "field-two-name",
    "database": {},
    "notification": {}
  }
]
~~~

### Database Types
The function has support for one database type as described below, where more are coming. To differentiate these types, a `type` field can be specified in the `database` dictionary.
~~~json
{
  "type": "database-type"
}
~~~

#### Datastore
The [Google Cloud Platform Datastore](https://cloud.google.com/datastore/docs/how-to) can be used to retrieve
 filtered data. To use this type, three fields are required within the database object:
- `type` `[string]`: the database type used, in this case `datastore`;
- `kind` `[string]`: the Datastore Kind that holds the data;
- `filters` `[dict]`: a dictionary containing [filters](https://cloud.google.com/datastore/docs/concepts/queries#filters) for the Datastore. There has to be a minimum of 1 filter.
 
The filters can be used as `"field": "filter-value"` and will be applied as matching filter:
~~~json
{
  "type": "datastore",
  "kind": "ErrorKind",
  "filters": {
    "field": "some-value",
    "field.subfield": "another-value"
  }
}
~~~

##### Optional fields
Within the Datastore type some optional fields can be specified:
- `time_field` `[string]`: a field that will be used to create a timedelta based on the [passed interval](#triggering-the-function).

<br />

### Notification Types
To send the notification via the correct platform each notification can be configured specifically to a notification type. For now, only one notification type can be used as described below but more are coming.
~~~json
{
  "type": "notification-type"
}
~~~

#### E-mail
The notification can be sent as an email via Gmail. Internally the function uses the Gmail SDK to send these mails and needs a GCP service account with [domain-wide delegation](https://developers.google.com/admin-sdk/directory/v1/guides/delegation) to access this SDK.

To enable this type the config below has to be put into the notification object of the configuration (see [config.example.py](config.example.py) for an example):
~~~json
{
  "type": "mail",
  "receiver": "receiver@example.com",
  "title": "An email title"
}
~~~

Furthermore, a credentials file named `gmailsdk_credentials.enc` must be present in the function (encrypted via [Google Cloud KMS](https://cloud.google.com/kms/docs/encrypt-decrypt)) that contains the credentials of the domain-wide delegated service account. The KMS Keyring is specified as `<PROJECT_ID>-keyring` and the key itself as `gmail-sdk-key`.

The function contains a HTML mail template, based on a [Velocity](http://velocity.apache.org/engine/1.7/user-guide.html) template, that will be filled with the error message(s). This file will be send towards the specified email address.

<br />

## Deploying the function
To deploy the function to the Google Cloud Platform, a build step has to be specified within the `cloudbuild.yaml` (see [cloudbuild.example.yaml](cloudbuild.example.yaml) for an example). The step described below will deploy the function towards the cloud platform:
~~~yaml
gcloud functions deploy ${PROJECT_ID}-error-notifier-func \
  --entry-point=error_to_notification \
  --runtime=python37 \
  --trigger-http \
  --project=${PROJECT_ID} \
  --region=europe-west1 \
  --max-instances=1
~~~

Make sure the required files are copied into the directory before deployment: `config.py` and `gmailsdk_credentials.enc`.

<br />

## Triggering the function
The function is triggered via a Google Cloud Scheduler and can be deployed using a `cloudbuild.yaml`. To deploy this function the next Cloud Build step can be specified within a `cloudbuild.yaml` (see [cloudbuild.example.yaml](cloudbuild.example.yaml) for an example).
~~~yaml
gcloud scheduler jobs delete ${PROJECT_ID}-errornotifier-job --quiet || true
gcloud scheduler jobs create http ${PROJECT_ID}-errornotifier-job \
  --schedule="0 * * * *" \
  --uri=https://europe-west1-${PROJECT_ID}.cloudfunctions.net/${PROJECT_ID}-error-notifier-func/ \
  --http-method=POST \
  --oidc-service-account-email=${PROJECT_ID}@appspot.gserviceaccount.com \
  --oidc-token-audience=https://europe-west1-${PROJECT_ID}.cloudfunctions.net/${PROJECT_ID}-error-notifier-func
~~~

Within the function a standard interval of `60m` is specified, and used when declaring the optional `database` attribute `time_field` ([see explanation](#optional-fields)). To use a different interval, a body can be send with the Cloud Scheduler specifying the interval in minutes where the scheduler will run every two hours as described below:
~~~yaml
--schedule="0 */2 * * *"
--message-body="{\"interval\": 120}"
~~~

##### IAM-policy
To make sure the Cloud Scheduler can invoke the function, the next script can be used to allow this:
~~~yaml
gcloud functions add-iam-policy-binding ${PROJECT_ID}-error-notifier-func \
  --region=europe-west1 \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/cloudfunctions.invoker"
~~~ 

<br />  

## License
This function is licensed under the [GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html) License
