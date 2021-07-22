import datetime
import operator
import re
from functools import reduce

import config
from google.cloud import datastore


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()

    def process(self, payload):
        # Set some variables
        project_id = self.get_project_id(payload)
        create_time = payload["finding"]["createTime"]
        notification_id = payload["finding"]["name"]
        recommendation = payload["finding"]["sourceProperties"]["Recommendation"]
        category = payload["finding"]["category"]

        # Create Datastore entity
        key = "{}".format(notification_id)
        entity_key = self.client.key(config.DB_SCC_NOTIFICATIONS_KIND, key)
        entity = self.client.get(entity_key)

        if entity is None:
            entity = datastore.Entity(key=entity_key)

        # Update status
        entity.update(
            {
                "project_id": project_id,
                "category": category,
                "created": create_time,
                "updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "recommendation": recommendation,
                "source": payload,
            }
        )

        self.client.put(entity)

    @staticmethod
    def get_project_id(payload):
        """
        Retrieve Project ID from current notification

        :param payload: Payload

        :return: Project ID
        :rtype: str
        """

        if get_from_dict(payload, ["resource", "projectDisplayName"]):
            return get_from_dict(payload, ["resource", "projectDisplayName"])

        if get_from_dict(payload, ["findings", "resourceName"]):
            try:
                return re.search(
                    r"/projects/([a-zA-Z0-9-]*)/",
                    str(get_from_dict(payload, ["findings", "resourceName"])),
                ).group(1)
            except AttributeError:
                pass

        return None


def get_from_dict(data_dict, map_list):
    """Returns a dictionary based on a mapping"""

    try:
        return reduce(operator.getitem, map_list, data_dict)
    except KeyError:
        return None
