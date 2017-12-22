from flask_socketio import SocketIO, send, emit, disconnect
from flask_login import current_user, LoginManager, login_user, \
    login_required, logout_user
from functools import wraps
from flask import Flask, request, Response, redirect
from flask_sslify import SSLify
import ssl
import time
import json
from mycroft.microservices.base import nice_json
from flask_sqlalchemy import SQLAlchemy
from os.path import join, dirname, realpath


def root_dir():
    """ Returns root directory for this project """
    return dirname(realpath(__file__ + '/.'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
socketio = SocketIO(app)


# user log in and auth
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.nickname)


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Api Key Required"'})


def check_auth(api_key):
    """This function is called to check if a api key is valid."""
    user = User.query.filter_by(id=api_key).first()
    if user is None:
        return False
    # TODO update db with timestamp
    return True


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' users = api keys '''
    auth = request.headers.get('Authorization', '')
    if not auth or not check_auth(auth):
        return authenticate()
    # Login and validate the user.
    # user should be an instance of your `User` class
    user = User.query.filter_by(id=auth).first()
    login_user(user)
    return nice_json({
        "uri": "/login",
        "welcome to jarbas server": {
            "login": "success"
        }
    })


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("https://patreon.com/jarbasAI")


# websocket for mycroft coms
@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        emit('my response',
             {'message': '{0} has connected'.format(current_user.name)})
    else:
        return False  # not allowed here


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    pass


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message)


@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    send(json, json=True)


# logged in websocket
@socketio.on('my event')
@authenticated_only
def handle_my_custom_event(json):
    emit('my response', json)


if __name__ == '__main__':
    login_manager.init_app(app)
    socketio.run(app)
