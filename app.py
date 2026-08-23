
import os  # lets us read environment variables (settings from outside the code)

from flask import Flask, request, jsonify 
from reputation_screening import screen_batch

# Create the Flask web application.
app = Flask(__name__)


# The network port this service listens on.
PORT = int(os.environ.get("PORT", "8072"))


@app.after_request
def add_cors_headers(response):
    # The web page runs on a different address (port 8080) from this service,
    # so browsers block the request by default for security. This header tells
    # the browser "it's fine, let them talk to me". (CORS = Cross-Origin
    # Resource Sharing.)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response



@app.route("/", methods=["GET"])
def screen():
    # Read the "items" value from the web address.
    # For  /screen?items=5000-1234-UK,200-4321-US  this gives us that text.
    # If "items" is missing, we use "" (an empty string) instead.
    items = request.args.get("items", "")


    # Hand the text to our checker and get back the results.
    result = screen_batch(items)

    # jsonify turns our Python dictionary into a proper JSON web response.
    return jsonify(result)


# A simple "are you alive?" endpoint. Handy for testing and for Docker.
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# This block only runs when we start the file directly with `python app.py`.
if __name__ == "__main__":
    # host="0.0.0.0" means "accept connections from anywhere", which is needed
    # so the service is reachable from outside its Docker container.
    app.run(host="0.0.0.0", port=PORT)
