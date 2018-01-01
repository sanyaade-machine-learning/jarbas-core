from mycroft.microservices.base import *
from mycroft.skills.intent_service import IntentService
from mycroft.util import LOG
from mycroft.util.parse import normalize
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
from threading import Thread
from time import sleep

ws = None
waiting = False
user_id = ""
answer_utt = ""
answer = None

intents = None
timeout = 60


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


@app.route("/ask/<lang>/<utterance>", methods=['GET'])
@noindex
@btc
@requires_auth
def ask(utterance, lang="en-us"):
    global user_id, answer_utt, answer
    ip = request.remote_addr
    user = request.headers["Authorization"]
    data = {"utterances": [utterance], "lang": lang}
    user_id = str(ip) + ":" + str(user)
    context = {"source": ip, "target": user, "user_id": user_id}
    message = Message("recognizer_loop:utterance", data, context)
    result = get_answer(message, "speak", context)
    # reset vars
    answer = None
    answer_utt = ""
    user_id = ""
    return nice_json(result)


def get_answer(message=None, reply="speak", context=None):
    global ws, answer, waiting, timeout
    answer = None
    # capture this reply
    ws.on(reply, listener)
    # emit message
    ws.emit(message)
    # correct answer context

    waiting = True
    # wait until timeout, complete failure or enf of event handler signal
    start = time.time()
    while waiting and time.time() - start < timeout:
        sleep(0.1)
    waiting = False

    answer = answer or Message("speak", {"utterance": "server timed out"},
                             context)
    if not answer.context:
        answer.context = {}
        answer.context["target"] = context["source"]
        answer.context["source"] = "https_server"

    # serialize into json
    answer = answer.serialize()
    # stop listening for this kind of reply
    ws.remove(reply, listener)
    return answer


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


def listener(message):
    global answer, user_id, answer_utt
    message.context = message.context or {}
    if message.context.get("user_id", "") == user_id:
        message.context["source"] = "https_server"
        if "utterance" in message.data.keys() and answer_utt:
            message.data["utterance"] = answer_utt + ". " + message.data["utterance"]
        answer_utt = message.data["utterance"]
        # use last message, update utterance only
        answer = message


def end_wait(message):
    global answer, waiting
    if not waiting:
        return
    if message.type == "complete_intent_failure":
        answer = Message("speak", {"utterance": "i have no idea how to "
                                                "answer that"})
    # no answer but end of handler
    elif answer is None:
        answer = Message("speak", {"utterance": "something went wrong, "
                                                "ask me later"})
    waiting = False

if __name__ == "__main__":
    global app, ws
    # connect to internal mycroft
    ws = WebsocketClient()
    ws.on("mycroft.skill.handler.complete", end_wait)
    ws.on("complete_intent_failure", end_wait)
    event_thread = Thread(target=connect)
    event_thread.setDaemon(True)
    event_thread.start()
    port = 6712
    start(app, port)
