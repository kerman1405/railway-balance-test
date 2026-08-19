import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

RAILWAY_API = "https://backboard.railway.com/graphql/v2"


def railway_request(query, variables=None):
    token = os.getenv("RAILWAY_API_TOKEN")

    if not token:
        raise Exception("RAILWAY_API_TOKEN is not set")

    response = requests.post(
        RAILWAY_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "variables": variables or {},
        },
        timeout=20,
    )

    try:
        result = response.json()
    except Exception:
        return {
            "http_status": response.status_code,
            "raw_response": response.text,
        }

    return {
        "http_status": response.status_code,
        "result": result,
    }


TEST_QUERY = """
query {
  usage(
    workspaceId: "d3fc859b-4843-4b32-ad35-10eef9a3cbca"
    measurements: [CPU_USAGE, MEMORY_USAGE_GB, NETWORK_RX_GB, NETWORK_TX_GB]
  ) {
    measurement
    value
  }

  estimatedUsage(
    workspaceId: "d3fc859b-4843-4b32-ad35-10eef9a3cbca"
    measurements: [CPU_USAGE, MEMORY_USAGE_GB, NETWORK_RX_GB, NETWORK_TX_GB]
  ) {
    measurement
    estimatedValue
  }
}
"""


@app.route("/")
def index():
    return "Railway Balance Test is running"


@app.route("/test")
def test():
    return jsonify(
        railway_request(TEST_QUERY)
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))

    app.run(
        host="0.0.0.0",
        port=port
    )
