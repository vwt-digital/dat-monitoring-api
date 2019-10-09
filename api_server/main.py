import logging

import openapi_server
from Flask_AuditLog import AuditLog
from Flask_No_Cache import CacheControl

try:
    import googleclouddebugger

    googleclouddebugger.enable()
except ImportError:
    pass

app = openapi_server.app

logging.basicConfig(level=logging.INFO)

AuditLog(app)
CacheControl(app)
