#!/usr/bin/env python3
import os

import connexion
from flask_cors import CORS
import config

from openapi_server import encoder

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Monitoring'},
            pythonic_params=True)
if 'GAE_INSTANCE' in os.environ:
    CORS(app.app, origins=config.ORIGINS)
else:
    CORS(app.app)
