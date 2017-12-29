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
 external single requests by https for mycroft functionality

requires an API key

- adapt intent determination
- stt
- tts
- ask mycroft (queues and answers by order)

status: nearly finished


# websockets

a websocket connection for asynchronous interface, this is a combination of
server + client service that bridge 2 mycroft instances, messages can be sent back and forth
between mycroft instances real time

these services check every message context field to see if they should be
forwarded to a client/server, a secure websocket connection is shared between
a server and a client, this is not the same internal mycroft websocket and is
authenticated separately


status: started

