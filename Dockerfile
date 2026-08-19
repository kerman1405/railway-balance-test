FROM ghcr.io/xtls/xray-core:latest AS xray

FROM python:3.12-alpine

RUN apk add --no-cache ca-certificates

COPY --from=xray /usr/local/bin/xray /usr/local/bin/xray

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
