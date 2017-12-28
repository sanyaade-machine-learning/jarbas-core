from flask_socketio import SocketIO, send, emit, disconnect
from flask_login import current_user, LoginManager, login_user, \
    login_required, logout_user
from functools import wraps
from flask import Flask, request, Response, redirect, session
from flask_sslify import SSLify
from eventlet.green import ssl
import time
import json
import base64
from datetime import timedelta
from mycroft.microservices.base import nice_json
from flask_sqlalchemy import SQLAlchemy
from os.path import join, dirname, realpath


def root_dir():
    """ Returns root directory for this project """
    return dirname(realpath(__file__ + '/.'))

port = 5678
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = "I LOVE BITCOIN"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
# auto https, incompatible with sockets
#sslify = SSLify(app)
socketio = SocketIO(app)


# user log in and auth
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    api = db.Column(db.String(120), index=True, unique=True)

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

    def __eq__(self, other):
        '''
        Checks the equality of two `User` objects using `get_id`.
        '''
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        '''
        Checks the inequality of two `User` objects using `get_id`.
        '''
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level.\n'
        'You have to obtain an API Key', 401,
        {'WWW-Authenticate': 'Basic realm="Api Key Required"'})


def check_auth(api_key):
    """This function is called to check if a api key is valid."""
    user = User.query.filter_by(api=api_key).first()
    if user is None:
        return False
    # TODO update db with timestamp
    return True


# @login_required does not work for websocket
def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            # keep session login alive
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=15)
            return f(*args, **kwargs)
    return wrapped


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key)
        if user:
            return user.first()

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        user = User.query.filter_by(api=api_key)
        if user:
            return user.first()

    # finally, return None if both methods did not login the user
    return None


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


@app.route('/login')
def login():
    ''' users = api keys '''
    api = request.headers.get('Authorization', '')
    if not api or not check_auth(api):
        return authenticate()
    # Login and validate the user.
    user = User.query.filter_by(api=api).first()
    login_user(user)
    return nice_json({
        "uri": "/login",
        "welcome to jarbas server": {
            "login": True
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


# require log in websocket
@socketio.on('ask_mycroft')
@authenticated_only
def handle_mycroft(message):
    # TODO actually ask mycroft and capture answer
    json = {"echo": message}
    emit('my response', json)


@app.route('/')
def index():
    return "Welcome to the Mycroft Collective"


def start(port=6666):
    global app
    cert = "{}/certs/JarbasServer.crt".format(root_dir())
    key = "{}/certs/JarbasServer.key".format(root_dir())
    version = ssl.PROTOCOL_TLSv1_2
    cert_reqs = ssl.CERT_NONE
    # lost too much time with self signed certs bug hunting, testing with http
    socketio.run(app=app, host="127.0.0.1", port=port, debug=False)#,
                 #keyfile=key, certfile=cert, cert_reqs=cert_reqs,
                 #ssl_version=version)


if __name__ == "__main__":
    start(port)
