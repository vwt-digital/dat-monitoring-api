#!/usr/bin/env bash
docker run --rm -v "${PWD}":/local openapitools/openapi-generator-cli generate \
--skip-overwrite \
-i /local/openapi_server/openapi/openapi.yaml \
-g python-flask \
-o /local

for f in openapi_server/models/*.py; do
  if ! grep -q '# flake8: noqa' "$f"; then
    echo '# flake8: noqa' >>"$f"
  fi
done
