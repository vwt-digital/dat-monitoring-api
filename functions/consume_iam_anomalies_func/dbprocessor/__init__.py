from hashlib import sha256

import config
from google.cloud import datastore


class DBProcessor(object):
    def __init__(self):
        self.client = datastore.Client()

    def process(self, payload):
        for anomaly in payload.get("iam_anomalies", []):
            # Create anomaly ID
            anomaly_id = (
                f"{anomaly['project_id']}_{anomaly['role']}_{anomaly['member']}"
            )
            key = sha256(str(anomaly_id).encode("utf-8")).hexdigest()

            # Create entity object
            entity_to_create = {
                "id": anomaly_id,
                "project_id": anomaly["project_id"],
                "role": anomaly["role"],
                "member": anomaly["member"],
                "updated_at": anomaly["reported_at"],
            }

            # Create Datastore entity
            entity_key = self.client.key(config.DB_SCC_NOTIFICATIONS_KIND, key)
            entity = self.client.get(entity_key)

            if entity is None:
                entity = datastore.Entity(key=entity_key)
                entity_to_create["created_at"] = anomaly["reported_at"]

            # Update status
            entity.update(entity_to_create)

            self.client.put(entity)
