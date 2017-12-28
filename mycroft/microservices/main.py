from mycroft.microservices.base import *
from mycroft.skills.intent_service import IntentService
from mycroft.util import LOG
from mycroft.util.parse import normalize
from mycroft.messagebus.client.ws import WebsocketClient
from threading import Thread

ws = None
intents = None


def connect():
    global ws
    ws.run_forever()


@app.route("/intent/<lang>/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def intent(utterance, lang="en-us"):
    result = {}
    try:
        # normalize() changes "it's a boy" to "it is boy", etc.
        best_intent = next(intents.engine.determine_intent(
            normalize(utterance, lang), 100,
            include_tags=True,
            context_manager=intents.context_manager))
        # TODO - Should Adapt handle this?
        best_intent['utterance'] = utterance
        result = best_intent
    except StopIteration:
        # don't show error in log
        pass
    except Exception as e:
        LOG.exception(e)
    return nice_json(result)


@app.route("/ask/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def ask(utterance):
    print request
    result = {"error": "not implemented", "echo": utterance}
    return nice_json(result)


@app.route("/stt/recognize", methods=['PUT'])
@noindex
@btc
@requires_auth
def stt():
    file_data = request.data
    path = "{}/stt.wav".format(root_dir())
    with open(path, "wb") as f:
        f.write(file_data)
    result = {"error": "not implemented"}
    return nice_json(result)


@app.route("/tts/<voice>/<sentence>", methods=['GET'])
@noindex
@btc
@requires_auth
def tts(voice, sentence):
    result = {"error": "not implemented"}
    return nice_json(result)


if __name__ == "__main__":
    global app, ws
    # connect to internal mycroft
    ws = WebsocketClient()
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()

    intents = IntentService(ws)
    port = 6712
    start(app, port)
