from os.path import exists, dirname
from threading import Thread
import os
import json
from twisted.internet import reactor, ssl
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG as logger
from mycroft.configuration import Configuration
from mycroft.util.ssl.self_signed import create_self_signed_cert

author = "jarbas"

NAME = Configuration.get().get("server", {}).get("name", "JarbasServer")


# TODO move into a sql db in some other code
def root_dir():
    """ Returns root directory for this project """
    return os.path.dirname(os.path.realpath(__file__ + '/.'))

with open("{}/database/users.json".format(root_dir()), "r") as f:
    users = json.load(f)


# protocol
class JarbasServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        logger.info("Client connecting: {0}".format(request.peer))
        # validate user

        api = request.headers.get("api")
        if api not in users:
            raise ValueError("Invalid API key")
        # send message to internal mycroft bus
        ip = request.peer.split(":")[1]
        data = {"ip": ip, "headers": request.headers}
        self.factory.emitter_send("client.connect", data)
        # return a pair with WS protocol spoken (or None for any) and
        # custom headers to send in initial WS opening handshake HTTP response
        headers = {"server": NAME}
        return (None, headers)

    def onOpen(self):
        """
       Connection from client is opened. Fires after opening
       websockets handshake has been completed and we can send
       and receive messages.

       Register client in factory, so that it is able to track it.
       """
        self.factory.register_client(self)
        logger.info("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            logger.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            logger.info("Text message received: {0}".format(payload.decode('utf8')))

        self.factory.process_message(self, payload, isBinary)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister_client(self, reason=u"connection closed")
        logger.info("WebSocket connection closed: {0}".format(reason))
        ip = self.peer.split(":")[1]
        data = {"ip": ip, "code": code, "reason": "connection closed", "wasClean": wasClean}
        self.factory.emitter_send("client.disconnect", data)

    def connectionLost(self, reason):
        """
       Client lost connection, either disconnected or some error.
       Remove client from list of tracked connections.
       """
        self.factory.unregister_client(self, reason=u"connection lost")
        logger.info("WebSocket connection lost: {0}".format(reason))
        ip = self.peer.split(":")[1]
        data = {"ip": ip, "reason": "connection lost"}
        self.factory.emitter_send("client.disconnect", data)


# server internals
class JarbasServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super(JarbasServerFactory, self).__init__(*args, **kwargs)
        # list of clients
        self.clients = {}
        # mycroft_ws
        self.emitter = None
        self.emitter_thread = None
        self.create_internal_emitter()

    def emitter_send(self, type, data=None, context=None):
        data = data or {}
        context = context or {}
        self.emitter.emit(Message(type, data, context))

    def connect_to_internal_emitter(self):
        self.emitter.run_forever()

    def create_internal_emitter(self):
        # connect to mycroft internal websocket
        self.emitter = WebsocketClient()
        self.register_internal_messages()
        self.emitter_thread = Thread(target=self.connect_to_internal_emitter)
        self.emitter_thread.setDaemon(True)
        self.emitter_thread.start()

    def register_internal_messages(self):
        self.emitter.on('speak', self.handle_speak)
        self.emitter.on('complete_intent_failure', self.handle_failure)

    # websocket handlers
    def register_client(self, client):
        """
       Add client to list of managed connections.
       """
        logger.info("registering client: " + str(client.peer))
        t, ip, sock = client.peer.split(":")
        # see if blacklisted
        if ip in self.ip_list and self.ip_blacklist:
            logger.warning("Blacklisted ip tried to connect: " + ip)
            self.unregister_client(client, reason=u"Blacklisted ip")
            return
        elif ip not in self.ip_list and not self.ip_blacklist:
            logger.warning("Unknown ip tried to connect: " + ip)
            #  if not whitelisted kick
            self.unregister_client(client, reason=u"Unknown ip")
            return
        self.clients[client.peer] = {"object": client, "status": "connected"}

    def unregister_client(self, client, code=3078, reason=u"unregister client request"):
        """
       Remove client from list of managed connections.
       """
        logger.info("deregistering client: " + str(client.peer))
        if client.peer in self.clients.keys():
            client_data = self.clients[client.peer]
            j, ip, sock_num = client.peer.split(":")
            context = {"user": client_data.get("names", ["unknown_user"])[0],
                       "source": ip + ":" + str(sock_num)}
            self.emitter.emit(
                Message("user.disconnect",
                        {"reason": reason, "ip": ip, "sock": sock_num},
                        context))
            client.sendClose(code, reason)
            self.clients.pop(client.peer)

    def process_message(self, client, payload, isBinary):
        """
       Process message from client, decide what to do internally here
       """
        logger.info("processing message from client: " + str(client.peer))
        client_data = self.clients[client.peer]
        client_type, ip, sock_num = client.peer.split(":")

    # mycroft handlers
    def handle_speak(self, message):
        pass

    def handle_failure(self, message):
        pass

if __name__ == '__main__':

    # server
    config = Configuration.get().get("server", {})
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 5678)
    max_connections = config.get("max_connections", -1)
    adress = u"wss://" + unicode(host) + u":" + unicode(port)
    cert = config.get("cert_file",
                      dirname(__file__) + '/certs/JarbasServer.crt')
    key = config.get("key_file",
                     dirname(__file__) + '/certs/JarbasServer.key')

    factory = JarbasServerFactory(adress)
    factory.protocol = JarbasServerProtocol
    if max_connections >= 0:
        factory.setProtocolOptions(maxConnections=max_connections)

    if not exists(key) or not exists(cert):
        logger.warning("ssl keys dont exist, creating self signed")
        dir = dirname(__file__) + "/certs"
        name = key.split("/")[-1].replace(".key", "")
        create_self_signed_cert(dir, name)
        cert = dir + "/" + name + ".crt"
        key = dir + "/" + name + ".key"
        logger.info("key created at: " + key)
        logger.info("crt created at: " + cert)
        # update config with new keys
        config["cert_file"] = cert
        config["key_file"] = key
        factory.config_update({"jarbas_server": config}, True)

    # SSL server context: load server key and certificate
    contextFactory = ssl.DefaultOpenSSLContextFactory(key, cert)

    reactor.listenSSL(port, factory, contextFactory)
    reactor.run()