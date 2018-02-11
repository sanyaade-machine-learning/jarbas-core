from twisted.internet import reactor, ssl

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol
from twisted.internet.protocol import ReconnectingClientFactory

import json
import sys
from threading import Thread
import hclib
import logging

logger = logging.getLogger("Standalone_Mycroft_Client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel("INFO")

platform = "JarbasHackChatClientv0.1"


class JarbasClientProtocol(WebSocketClientProtocol):
    hackchat = None
    online_users = []
    connector = None

    def start_hack_chat(self):
        self.hackchat = hclib.HackChat(self.on_hack_message, "Jarbas",
                                       "Jarbasai")

    # Make a callback function with two parameters.
    def on_hack_message(self, connector, data):
        # The second parameter (<data>) is the data received.
        self.connector = connector
        self.online_users = connector.onlineUsers
        # Checks if someone joined the channel.
        if data["type"] == "online add":
            # Sends a greeting the person joining the channel.
            #
            connector.send("Hello {}".format(data["nick"]))
        if data["type"] == "message":
            utterance = data["text"]
            user = data["nick"]
            msg = {"data": {"utterances": [utterance], "lang": "en-us"},
                   "type": "recognizer_loop:utterance",
                   "context": {"source": self.peer, "destinatary":
                       "https_server", "platform": platform,
                               "hack_chat_nick": user, "user": user}}
            msg = json.dumps(msg)
            self.sendMessage(msg, False)

    def onConnect(self, response):
        logger.info("Server connected: {0}".format(response.peer))

    def onOpen(self):
        logger.info("WebSocket connection open. ")
        self.chat_thread = Thread(target=self.start_hack_chat)
        self.chat_thread.setDaemon(True)
        self.chat_thread.start()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            msg = json.loads(payload)
            print msg
            user = msg.get("context", {}).get("hack_chat_nick", "")
            if user not in self.online_users:
                logger.info("invalid hack chat user: " + user)
                return
            utterance = ""
            if msg.get("type", "") == "speak":
                utterance = msg["data"]["utterance"]
            elif msg.get("type", "") == "complete_intent_failure":
                utterance = "i can't answer that yet"
            if utterance:
                utterance = "@{} , ".format(user) + utterance
                logger.info("Sent: " + utterance)
                self.connector.send(utterance)
        else:
            pass

    def onClose(self, wasClean, code, reason):
        logger.info("WebSocket connection closed: {0}".format(reason))
        self.hackchat.leave()
        self.input_loop.join()
        self.chat_thread.join()


class JarbasClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = JarbasClientProtocol

    def __init__(self, *args, **kwargs):
        super(JarbasClientFactory, self).__init__(*args, **kwargs)
        self.status = "disconnected"

    # websocket handlers
    def clientConnectionFailed(self, connector, reason):
        logger.info("Client connection failed: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.info("Client connection lost: " + str(reason) + " .. retrying ..")
        self.status = "disconnected"
        self.retry(connector)


if __name__ == '__main__':
    import base64
    host = "165.227.224.64"
    port = 5678
    name = "standalone cli client"
    api ="test_key"
    authorization = name+":"+api
    usernamePasswordDecoded = authorization
    api = base64.b64encode(usernamePasswordDecoded)
    headers = {'authorization': api}
    adress = u"wss://" + host + u":" + str(port)
    factory = JarbasClientFactory(adress, headers=headers,
                                  useragent=platform)
    factory.protocol = JarbasClientProtocol
    contextFactory = ssl.ClientContextFactory()
    reactor.connectSSL(host, port, factory, contextFactory)
    reactor.run()