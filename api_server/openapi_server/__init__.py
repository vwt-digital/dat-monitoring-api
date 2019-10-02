#!/usr/bin/env python3
from threading import Thread

import connexion
from flask_cors import CORS
from flask import request

from openapi_server import encoder

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Monitoring'},
            pythonic_params=True)
CORS(app.app)
