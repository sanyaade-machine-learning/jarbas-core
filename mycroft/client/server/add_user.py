from mycroft.client.server.main import db, User
from mycroft.microservices import gen_api

user = User(nickname="test", api=gen_api("test", False))
db.create_all()
db.session.add(user)
db.session.commit()