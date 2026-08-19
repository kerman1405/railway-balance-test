import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

RAILWAY_API = "https://backboard.railway.com/graphql/v2"


def railway_request(query, variables=None):
    token = os.getenv("RAILWAY_API_TOKEN")

    if not token:
        raise Exception("RAILWAY_API_TOKEN is not set")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        RAILWAY_API,
        headers=headers,
        json={
            "query": query,
            "variables": variables or {},
        },
        timeout=20,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise Exception(result["errors"])

    return result["data"]


# پیدا کردن Workspaceهای قابل دسترسی
WORKSPACES_QUERY = """
query {
  me {
    workspaces {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
"""


# دریافت Usage مربوط به Workspace
USAGE_QUERY = """
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
    try:
        # 1. پیدا کردن Workspace
        workspace_data = railway_request(WORKSPACES_QUERY)

        workspaces = (
            workspace_data
            .get("me", {})
            .get("workspaces", {})
            .get("edges", [])
        )

        if not workspaces:
            return jsonify({
                "error": "No workspace found"
            }), 404

        workspace = workspaces[0]["node"]

        workspace_id = workspace["id"]
        workspace_name = workspace["name"]

        # 2. گرفتن Usage
        usage_data = railway_request(
            USAGE_QUERY,
            {
                "workspaceId": workspace_id
            }
        )

        return jsonify({
            "workspace": {
                "id": workspace_id,
                "name": workspace_name
            },
            "usage": usage_data.get("usage"),
            "estimatedUsage": usage_data.get("estimatedUsage")
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(
        host="0.0.0.0",
        port=port
    )
