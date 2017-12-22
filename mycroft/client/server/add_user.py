from mycroft.client.server.main import db, User
from mycroft.microservices import gen_api

user = User(nickname="test", email="no@mail.com", id=gen_api("test", False))
db.session.add(user)
db.session.commit()