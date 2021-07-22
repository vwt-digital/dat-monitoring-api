import base64
import json
import logging
from functools import reduce

import config
from gobits import Gobits
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()

logging.basicConfig(level=logging.INFO)
logging.getLogger("google.resumable_media._helpers").setLevel(level=logging.ERROR)


def get_issue_data(subscription, payload, type):
    issue_type = config.ISSUE_TITLES[subscription]
    variables = {}
    for key, value in issue_type["variables"].items():
        variable_value = get_variable_value(payload=payload, keys=value)
        if variable_value is None:
            # Makes sure that no invalid title can pass.
            return None
        variables[key] = variable_value
    return issue_type[type].format(**variables)


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
        # Check if there is a root in the payload
        root = config.ISSUE_TITLES[subscription].get("root", "")
        if root:
            # Check if root of payload is a list
            root_payload = payload.get(root)
            if not root_payload:
                logging.error(
                    f"A root was defined in the config for subscription {subscription} but it could not be found in the payload"
                )
            if isinstance(root_payload, list):
                for sub_payload in root_payload:
                    publish(subscription, sub_payload)
            else:
                publish(subscription, root_payload)
        else:
            publish(subscription, payload)

    # Returning any 2xx status indicates successful receipt of the message.
    # 204: no content, delivery successful, no further actions needed
    return "OK", 204


def publish(subscription, payload):
    title = get_issue_data(subscription=subscription, payload=payload, type="title")
    comment = get_issue_data(subscription=subscription, payload=payload, type="comment") if "comment" in \
                                                                                            config.ISSUE_TITLES[
                                                                                                subscription] else None
    description = get_issue_data(subscription=subscription, payload=payload, type="description") if "description" in \
                                                                                                    config.ISSUE_TITLES[
                                                                                                subscription] else None

    if not title:
        logging.exception(
            f"Failed to create title with {payload}."
            f"This is most likely not caused by the config, "
            f"but by an invalid payload provided by an external service."
        )
        return (
            "Unprocessable Entity",
            422,
        )

    formatted = json.dumps(
        {
            "gobits": [Gobits().to_json()],
            "issue": {
                "title": title,
                "category": config.ISSUE_TITLES[subscription].get("category", ""),
                "payload": description if description else payload,
                "comment": comment
            },
        },
        indent=2,
    ).encode("utf-8")

    # Publish to ops-issues here
    topic_path = publisher.topic_path(config.ODH_PROJECT, config.OPS_ISSUES)
    published = publisher.publish(topic_path, formatted)

    logging.info(f"Published message with id {published.result()}")
