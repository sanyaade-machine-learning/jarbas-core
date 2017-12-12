from functools import wraps
from flask import Flask, make_response
from flask import request, Response
import time
import os
import json
from mycroft.microservices import gen_api


def root_dir():
    """ Returns root directory for this project """
    return os.path.dirname(os.path.realpath(__file__ + '/.'))


def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response

app = Flask(__name__)
port = 5678


with open("{}/database/users.json".format(root_dir()), "r") as f:
    users = json.load(f)

with open("{}/database/admins.json".format(root_dir()), "r") as f:
    admins = json.load(f)


def add_response_headers(headers=None):
    """This decorator adds the headers passed in to the response"""
    headers = headers or {}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp

        return decorated_function

    return decorator


def noindex(f):
    """This decorator passes X-Robots-Tag: noindex"""
    return add_response_headers({'X-Robots-Tag': 'noindex'})(f)


def btc(f):
    """This decorator passes btc request """
    return add_response_headers({'BTC': '1aeuaAijzwK4Jk2ixomRkqjF6Q3JxXp9Q'})(
        f)


def check_auth(api_key):
    """This function is called to check if a api key is valid."""
    if api_key not in users:
        return False
    users[api_key]["last_active"] = time.time()
    with open("{}/database/users.json".format(root_dir()), "w") as f:
        f.write(json.dumps(users))
    return True


def check_admin_auth(api_key):
    """This function is called to check if a api key is valid."""
    if api_key not in admins:
        return False
    admins[api_key]["last_active"] = time.time()
    with open("{}/database/admins.json".format(root_dir()), "w") as f:
        f.write(json.dumps(admins))
    return True


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Api Key Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth or not check_auth(auth):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth or not check_admin_auth(auth):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route("/", methods=['GET'])
@noindex
@btc
@requires_auth
def hello():
    return nice_json({
        "uri": "/",
        "welcome to jarbas microservices": {
            "under": "construction"
        }
    })


@app.route("/api_add/<api>/<id>/<name>", methods=['PUT'])
@noindex
@btc
@requires_admin
def add_user(api, id, name):
    result = {"id": id, "last_active": 0, "name": name}
    users[api] = result
    with open("{}/database/users.json".format(root_dir()), "w") as f:
        f.write(json.dumps(users))
    return nice_json({
        result
    })


@app.route("/api_gen", methods=['GET'])
@noindex
@btc
@requires_admin
def gen_api():
    api = gen_api(save=False)
    return nice_json({
        {"api": api}
    })


def start(port=6666):
    global app
    app.run(port=port, debug=True)


if __name__ == "__main__":
    start(port)
