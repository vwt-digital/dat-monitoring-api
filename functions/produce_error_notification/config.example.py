# To monitor multiple errors, the list below provides all necessary fields to
# send the correct notification towards the correct receiver. Fields that are
# required are: active, id, message_field, notification.

# TODO: Expand description for config. (additional fields)


NOTIFICATION_CONFIG = [{
    "active": True,
    "id": "mail-notification-example",
    "message_field": "attribute",
    "notification": {
        "type": "mail",
        "receiver": "receiver@example.com",
        "title": "Notification example"
    },
    "datastore": {
        "kind": "datastore-kind",
        "filters": {
            "project_id": "project-id",
            "resource.type": "cloud_function",
            "resource.labels.function_name": "function-name"
        }
    }
}]
