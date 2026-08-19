import os
import base64
import requests

from flask import Flask, Response, jsonify

app = Flask(__name__)

RAILWAY_API = "https://backboard.railway.com/graphql/v2"


def get_env(name):
    value = os.getenv(name)

    if not value:
        raise Exception(f"{name} is not set")

    return value


def get_balance():

    token = get_env("RAILWAY_API_TOKEN")

    query = """
    query {
      me {
        workspaces {
          id
          name
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
            "Content-Type": "application/json"
        },
        json={
            "query": query
        },
        timeout=20
    )

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    workspaces = data["data"]["me"]["workspaces"]

    if not workspaces:
        raise Exception("No workspace found")

    # اولین Workspace اکانت Railway
    workspace = workspaces[0]

    customer = workspace.get("customer")

    if not customer:
        raise Exception("Customer information not found")

    return customer["remainingUsageCreditBalance"]


def make_vless_config(balance):

    domain = get_env("XRAY_DOMAIN")
    uuid = get_env("UUID")

    name = f"Xray Railway | Balance: ${balance:.2f}"

    vless = (
        f"vless://{uuid}@{domain}:443"
        f"/?path=%2Fxray"
        f"&security=tls"
        f"&encryption=none"
        f"&host={domain}"
        f"&type=ws"
        f"&sni={domain}"
        f"#{name}"
    )

    return vless


@app.route("/")
def home():

    return "Railway Xray Subscription Server is running"


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



@app.route("/sub")
def subscription():

    try:

        value = get_balance()

        vless = make_vless_config(value)

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
