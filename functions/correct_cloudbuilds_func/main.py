import logging
import datetime

from google.cloud import datastore
from flask import make_response, jsonify


def correct_cloudbuilds(request):
    if request.args and "kind" in request.args and "field" in request.args and "interval" in request.args:

        db_client = datastore.Client()
        batch = db_client.batch()
        query = db_client.query(kind=request.args["kind"])

        interval = int(request.args["interval"])
        logging.info(f"Auto-changing 'pending' builds older than {interval} hours")

        time_delta = (datetime.datetime.now() - datetime.timedelta(hours=interval)).isoformat()
        query.add_filter(request.args["field"], "<=", time_delta)
        query.add_filter("status", "=", "pending")
        query.keys_only()
        entities = query.fetch()

        batch_count_total = 0

        if entities:
            batch.begin()
            batch_count = 0

            for entity in entities:
                if batch_count == 500:
                    batch.commit()
                    batch = db_client.batch()
                    batch.begin()
                    batch_count = 0

                entity['status'] = 'failing'
                entity['status_original'] = 'AUTO_FAILURE'

                batch.put(entity)
                batch_count += 1
                batch_count_total += 1

            batch.commit()

        logging.info(f"Updated total of {batch_count_total} entities")
        return make_response("No Content", 204)
    else:
        problem = {"type": "MissingParameters",
                   "title": "Expected kind, hours interval and field for deleting entities not found",
                   "status": 400}
        response = make_response(jsonify(problem), 400)
        response.headers["Content-Type"] = "application/problem+json",
        return response
