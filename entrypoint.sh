#!/bin/sh

set -e

: "${UUID:?UUID is required}"
: "${PORT:?PORT is required}"

sed "s/\${UUID}/${UUID}/g" /app/config.json > /tmp/xray.json


/usr/local/bin/xray run -config /tmp/xray.json &


python app.py
