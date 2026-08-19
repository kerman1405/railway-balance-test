import os
import json
import requests
from flask import Flask, jsonify

app = Flask(__name__)

RAILWAY_API = "https://backboard.railway.com/graphql/v2"

QUERY = """
query GetUsage($workspaceId: String!) {
  usage(workspaceId: $workspaceId) {
    measurement
    value
  }

  estimatedUsage(workspaceId: $workspaceId) {
    measurement
    estimatedValue
  }
}
"""


@app.route("/")
def index():
    return "Railway Balance Test is running"


@app.route("/usage")
def usage():
    token = os.getenv("RAILWAY_API_TOKEN")
    workspace_id = os.getenv("RAILWAY_WORKSPACE_ID")

    if not token:
        return jsonify({
            "error": "RAILWAY_API_TOKEN is not set"
        }), 500

    if not workspace_id:
        return jsonify({
            "error": "RAILWAY_WORKSPACE_ID is not set"
        }), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": QUERY,
        "variables": {
            "workspaceId": workspace_id
        }
    }

    response = requests.post(
        RAILWAY_API,
        headers=headers,
        json=payload,
        timeout=15
    )

    try:
        result = response.json()
    except Exception:
        return jsonify({
            "http_status": response.status_code,
            "raw_response": response.text
        }), 500

    return jsonify(result), response.status_code


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
