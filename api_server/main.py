import openapi_server

try:
    import googleclouddebugger

    googleclouddebugger.enable()
except ImportError:
    pass

app = openapi_server.app
