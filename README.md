[![CodeFactor](https://www.codefactor.io/repository/github/vwt-digital/dat-monitoring-api/badge)](https://www.codefactor.io/repository/github/vwt-digital/dat-monitoring-api)
# dat-monitoring-api
Dat-monitoring-api deploys functions and an API that make it possible to:
- Monitor errors and bugs in GCP projects.
- Monitor build issues in GCP projects.
- Monitor security issues in GCP projects.
- Format/parse and send issues.
- Retrieve issues to use in other projects.

### Setup & Installation
Installation of the monitoring api can be read [in the api README](https://github.com/vwt-digital/dat-monitoring-api/tree/master/api_server#usage).

Every functions located in `/functions` can be run separately from the API. Installation of the dependencies can be done by running `pip install -r requirements.txt`, except when otherwise specified in the function's README.

The function can be deployed by running the following command, except when otherwise specified in the function's README:
```
gcloud functions deploy ${PROJECT_ID}$${FUNCTION_NAME} \
     --entry-point=$${ENTRY_POINT} \
     --runtime=python37 \
     --trigger-http \
     --project=${PROJECT_ID} \
     --region=$${REGION} \
     --max-instances=1
```
* `${PROJECT_ID}` is the ID of the project, specified in GCP.
* `$${FUNCTION_NAME}` should be the name of the function.
* `$${ENTRY_POINT}` should be the name of the function within the cloud function.
* `$${REGION}` should be the region where the cloud function will be deployed.
