import base64
import json
import logging
from functools import reduce

import config
from gobits import Gobits
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()


def get_issue_title(title_type, payload):
    issue_type = config.ISSUE_TITLES[title_type]
    variables = {}
    for key, value in issue_type["variables"].items():
        variable_value = get_variable_value(payload=payload, keys=value)
        if variable_value is None:
            # Makes sure that no invalid title can pass.
            return None
        variables[key] = variable_value
    return issue_type["title"].format(**variables)


def check_conditions(title_type, payload):
    issue_type = config.ISSUE_TITLES[title_type]
    if "conditions" in issue_type:
        for condition in issue_type["conditions"]:
            if (
                get_variable_value(payload=payload, keys=condition["variable"])
                not in condition["shouldBe"]
            ):
                return False
    return True


def get_variable_value(payload, keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, payload)


def topic_to_topic(request):
    # Extract data from request
    envelope = json.loads(request.data.decode("utf-8"))
    payload = json.loads(base64.b64decode(envelope["message"]["data"]))

    # Extract subscription from subscription string
    try:
        subscription = envelope["subscription"].split("/")[-1]
        logging.info(f"Message received from {subscription} {payload}")
    except Exception as e:
        logging.info("Extract of subscription failed")
        logging.exception(e)
        return "Conflict", 409
    if not hasattr(config, "ISSUE_TITLES") or subscription not in config.ISSUE_TITLES:
        logging.info(
            f"Not formatting issue from {subscription} because of missing title subscription."
        )
    elif not check_conditions(title_type=subscription, payload=payload):
        logging.info(
            f"Not formatting issue from {subscription} because of failing conditions with {payload}"
        )
    else:
        title = get_issue_title(title_type=subscription, payload=payload)

        if not title:
            return (
                f"Failed to create title with {payload}."
                f"This is most likely not caused by the config, "
                f"but by an invalid payload provided by an external service.",
                422,
            )

        formatted = json.dumps(
            {
                "gobits": [Gobits().to_json()],
                "issue": {"title": title, "payload": payload},
            },
            indent=2,
        ).encode("utf-8")

        # Publish to ops-issues here
        topic_path = publisher.topic_path(config.ODH_PROJECT, config.OPS_ISSUES)
        publisher.publish(topic_path, formatted)

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successful, no further actions needed
    return "OK", 204
