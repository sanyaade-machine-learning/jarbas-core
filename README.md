# jarbas - server fork

bare bones backend based on [jarbas-dev](https://github.com/JarbasAl/jarbas-core/tree/dev). meant for server usage

* removed tts (to be re-added for microservice)
* removed stt (to be re-added for microservice)
* removed speech client + hotwords
* removed enclosure (to be re-added as avatar service)
* removed audio
* removed mimic install and no longer used requirements
* dummy enclosure api

some skills would no longer work/undesired and are blacklisted

* naptime - undesired
* alarm - TODO make version that works per user
* volume - undesired
* desktop launcher - undesired
* reminder - TODO make version that works per user

# micro services

for remote access to this server some endpoints are being created, these allow
 external single [requests by https](https://github.com/JarbasAl/jarbas-core/tree/server/mycroft/microservices) for mycroft functionality

requires an API key

    from mycroft.microservices.api import MycroftAPI

    ap = MycroftAPI("api_key")
    json_responde = ap.ask_mycroft("hello world")


# websockets

a websocket connection for asynchronous interface, this is a combination of
[server](https://github.com/JarbasAl/jarbas-core/blob/server/mycroft/client/server/main.py) + [client](https://github.com/JarbasAl/jarbas-core/blob/server/mycroft/client/server/client.py) service that bridge 2 mycroft instances, messages can
be sent back and forth between mycroft instances real time

these services check every message context field to see if they should be
forwarded to a client/server, a secure websocket connection is shared between
a server and a client, this is not the same internal mycroft websocket and is
authenticated separately

this allows for example client-mycroft to ask server for face recognition, or
server-mycroft to ask camera-mycroft for a picture

# Clients

turn anything with an internet connection into a mycroft endpoint

- any jarbas install can be a [full client](https://github.com/JarbasAl/jarbas-core/blob/server/mycroft/client/server/client.py)
- theres a standalone [command line input client](https://github.com/JarbasAl/jarbas-core/blob/server/mycroft/client/server/standalone_cli_client.py)
- theres a standalone [voice input client](https://github.com/JarbasAl/jarbas-core/blob/server/mycroft/client/server/standalone_voice_client.py)
- standalone/web [remi](https://github.com/dddomodossola/remi) client (webpage)
- local remi client (connects to a local instance)

# new bus messages

server side

        - client.connect - {"data": {"ip": "127.0.0.1", "headers": {"upgrade": "WebSocket", "sec-websocket-version": "13", "connection": "Upgrade", "sec-websocket-key": "s+OB2Be7AhCvEmYp299/mg==", "user-agent": "JarbasClientv0.1", "host": "0.0.0.0:5678", "api": "test_key", "pragma": "no-cache", "cache-control": "no-cache"}}, "type": "client.connect", "context": {"source": "tcp4:127.0.0.1:59856"}}
        - client.connection.error - {"data": {"ip": "127.0.0.1", "api_key": "test_kkkey", "error": "invalid api key"}, "type": "client.connection.error", "context": {"source": "tcp4:127.0.0.1:59856"}}
        - client.broadcast - TODO add example from logs
        - client.send - TODO add example from logs
        - client.send.error - TODO add example from logs
        - user.disconnect - {"data": {"ip": "127.0.0.1", "reason": "connection lost", "sock": "59856"}, "type": "user.disconnect", "context": {"source": "127.0.0.1:59856", "user": "unknown_user"}}
        - client.disconnect - {"data": {"ip": "127.0.0.1", "reason": "connection lost"}, "type": "client.disconnect", "context": {"source": "tcp4:127.0.0.1:59856"}}


client side

        - server.connected - {"data": {"server_id": "AutobahnPython/17.6.2, JarbasServer"}, "type": "server.connected", "context": null}
        - server.websocket.open - {"data": {}, "type": "server.websocket.open", "context": null}
        - server.message.received - TODO add example from logs
        - server.message.send - TODO add example from logs
        - server.complete_intent_failure - TODO add example from logs
        - server.connection.closed - {"data": {"wasClean": false, "code": 1006, "reason": "connection was closed uncleanly (peer dropped the TCP connection without previous WebSocket closing handshake)"}, "type": "server.connection.closed", "context": null}



# TODOS

        - SSL for remi
        - client in javascript that connects a browser websocket chat to a server-mycroft
        - adapt context field per user
        - converse per user
        - language selection per query

