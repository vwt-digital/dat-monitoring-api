# Format Issues
This function consumes messages containing issues posted on a Pub/Sub Topic, formats them to a specific format and sends them to another topic.

## Setup
1. Make sure a ```config.py``` file exists within the directory, based on the [config.py.example](config.py.example), with the correct configuration:
    ~~~
    ODH_PROJECT = Google Cloud Platform project where subscription is
    OPS_ISSUES = Google Cloud Platform subscription to send formatted messages to
    ISSUE_TITLES = A dictionary containing information on how to format the incoming messages
    ~~~
2. Deploy the function with help of the [cloudbuild.example.yaml](cloudbuild.example.yaml) to the Google Cloud Platform.

## Issue Titles
The variable ```ISSUE_TITLES``` can look as follows:
~~~JSON
{
    "subscription_title1": {
        "title": "Issue in project {project_id}",
        "variables": {"project_id": ["projectId"],
        "conditions": [
            {
              "variable": ["status"], 
              "shouldBe": ["FAILURE", "TIMEOUT", "CANCELLED"]
            }
        ],
        "category": "category1",
    },
    "subscription_title2": {
        "title": "Fix bug in {project_id} {issue_type}",
        "variables": {
            "project_id": ["resource", "project_id"],
            "issue_type": ["resource", "type"],
        },
        "category": "category2",
    },
    "subscription_title3": {
        "title": "Update code in {repository}",
        "variables": {
            "repository": ["repository"],
        },
        "category": "category1",
        "root": "repositories",
    },
}
~~~
Where ```title``` is a field in the formatted message and can contain variables between curly braces.
The variables in the title are gotten from the incoming message. To define what fields from the message should be used, use ```variables```.
If ```conditions``` is used, a ```variable``` from the incoming message can only have the values defined in ```shouldBe```.
```category``` can be used to send the field ```category``` in the incoming message.
```root``` can be used if the fields from the incoming message are under a root.

## Incoming message
The incoming message should be send from a ```subscription``` that is defined in the config.
To make sure the function works according to the way it was intented, the incoming messages from a Pub/Sub Topic must have the following structure based on the [company-data structure](https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema):
~~~JSON
{
  "gobits": [ ],
  "field1": "value1",
  "field2": "value2",
  "field_etcetera": "value_etcetera"
}
~~~

The message can also look as follows if the ```root``` variable is defined in the config
~~~JSON
{
  "gobits": [ ],
  "root": {
    "field1": "value1",
    "field2": "value2",
    "field_etcetera": "value_etcetera"
  }
}
~~~

Another way the message can look if the ```root``` variable is defined in the config is as follows:
~~~JSON
{
  "gobits": [ ],
  "root": [
    {
      "field1": "value1",
      "field2": "value2",
      "field_etcetera": "value_etcetera"
    }
  ]
}
~~~

An example message for ```subscription_title1``` and ```subscription_title2``` defined in the [example-config](config.py.example) can be:
~~~JSON
{
  "gobits": [ ],
  "project_id": "1",
  "status": "FAILURE",
  "resource": {
    "project_id": "1",
    "type": "a_type"
  }
}
~~~

An example message for ```subscription_title3``` defined in the [example-config](config.py.example) can be:
~~~JSON
{
  "gobits": [ ],
  "repositories": [
    {
      "repository": "a_repository"
    }
  ]
}
~~~

## License
This function is licensed under the [GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html) License
