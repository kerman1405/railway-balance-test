import os
import base64
import requests

from flask import Flask, Response, jsonify

app = Flask(__name__)

RAILWAY_API = "https://backboard.railway.com/graphql/v2"

WORKSPACE_ID = "d3fc859b-4843-4b32-ad35-10eef9a3cbca"

# اطلاعات واقعی Xray
XRAY_DOMAIN = os.getenv("XRAY_DOMAIN", "YOUR-RAILWAY-DOMAIN")
XRAY_UUID = os.getenv(
    "XRAY_UUID",
    "YOUR-UUID"
)


def get_balance():
    token = os.getenv("RAILWAY_API_TOKEN")

    if not token:
        raise Exception("RAILWAY_API_TOKEN is not set")

    query = """
    query {
      me {
        workspaces {
          id
          customer {
            remainingUsageCreditBalance
          }
        }
      }
    }
    """

    response = requests.post(
        RAILWAY_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"query": query},
        timeout=20,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise Exception(result["errors"])

    for workspace in result["data"]["me"]["workspaces"]:
        if workspace["id"] == WORKSPACE_ID:
            return workspace["customer"]["remainingUsageCreditBalance"]

    raise Exception("Workspace not found")


def make_vless_config(balance):
    name = f"Xray-Railway  | Balance: ${balance:.2f}"

    vless = (
        f"vless://{XRAY_UUID}@{XRAY_DOMAIN}:443"
        f"/?path=%2Fxray"
        f"&security=tls"
        f"&encryption=none"
        f"&host={XRAY_DOMAIN}"
        f"&type=ws"
        f"&allowInsecure=0"
        f"&sni={XRAY_DOMAIN}"
        f"#{name}"
    )

    return vless


@app.route("/")
def index():
    return "Railway Subscription Server is running"


@app.route("/balance")
def balance():
    try:
        value = get_balance()

        return jsonify({
            "balance": round(value, 4),
            "display": f"${value:.2f}"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/sub/<token>")
def subscription(token):

    if token != XRAY_UUID:
        return Response(
            "Invalid subscription token",
            status=404,
            mimetype="text/plain"
        )

    try:
        balance = get_balance()

        vless = make_vless_config(balance)

        encoded = base64.b64encode(
            vless.encode("utf-8")
        ).decode("utf-8")

        return Response(
            encoded,
            mimetype="text/plain"
        )

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
