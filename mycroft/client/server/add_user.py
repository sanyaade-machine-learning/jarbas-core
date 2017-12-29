from mycroft.client.server.socketio_mess import db, User
from mycroft.microservices import gen_api

user_id = User(nickname="test", api="test_key")
db.create_all()
db.session.add(user_id)
db.session.commit()