from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
from threading import Thread

from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG as logger
from mycroft.configuration import Configuration


class MyClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))
        self.factory.emitter.emit(Message("server.connected",
                                          {"server_id": response.headers[
                                              "server"]}))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.factory.emitter.emit(Message("server.websocket.open"))

    def onMessage(self, payload, isBinary):
        logger.info("status: " + self.factory.status)
        if isBinary:
            data = {"payload": payload, "isBinary": isBinary}
        else:
            data = {"payload": None, "isBinary": isBinary}
        self.factory.emitter.emit(Message("server.message.received",
                                  data))

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        self.factory.emitter.emit(Message("server.connection.closed",
                                  {"wasClean": wasClean,
                                   "reason": reason,
                                   "code": code}))

    def Message_to_raw_data(self, message):
        # convert a Message object into raw data that can be sent over
        # websocket
        if hasattr(message, 'serialize'):
            return message.serialize()
        else:
            return json.dumps(message.__dict__)


class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = MyClientProtocol

    def __init__(self, *args, **kwargs):
        super(MyClientFactory, self).__init__(*args, **kwargs)
        self.client = None
        self.status = "disconnected"
        # mycroft_ws
        self.emitter = None
        self.emitter_thread = None
        self.create_internal_emitter()

    # initialize methods
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
        self.emitter.on('recognizer_loop:utterance', self.handle_utterance)

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    # mycroft handlers
    def handle_speak(self, event):
        utterance = event.data.get('utterance')

    def handle_utterance(self, event):
        pass

    def sendRaw(self, data):
        if self.client is None:
            logger.error("Client is none")
            return
        self.client.sendMessage(data, isBinary=True)

    def sendMessage(self, type, data, context=None):
        if self.client is None:
            logger.error("Client is none")
            return
        if context is None:
            context = {}
        msg = self.client.Message_to_raw_data(Message(type, data, context))
        self.client.sendMessage(msg, isBinary=False)
        self.emitter.emit(Message("server.message.sent",
                                  {"type": type,
                                   "data": data,
                                   "context": context,
                                   "raw": msg}))


if __name__ == '__main__':

    config = Configuration.get().get("client", {})
    host = config.get("host", "0.0.0.0")
    port = config.get("port", 5678)
    api = config.get("api", "test_key")
    headers = {'API': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = MyClientFactory(adress, headers=headers)
    factory.protocol = MyClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()